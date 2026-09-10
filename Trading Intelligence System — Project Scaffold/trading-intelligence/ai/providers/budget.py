"""Budget controller — tracks and enforces monthly AI spending limits."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger("ai.budget")


class BudgetController:
    """Controls monthly AI budget spending.

    Tracks all API usage and enforces budget thresholds:
    - 80%: Reduce expensive model usage
    - 90%: Cloud usage minimized
    - 100%: Local-only mode
    """

    def __init__(self, monthly_budget: float | None = None):
        self.monthly_budget = monthly_budget or settings.monthly_ai_budget

    async def get_monthly_spending(self, db: AsyncSession) -> float:
        """Get total AI spending for the current month."""
        now = datetime.now(timezone.utc)
        result = await db.execute(
            text("""
                SELECT COALESCE(SUM(estimated_cost), 0) as total
                FROM api_usage
                WHERE EXTRACT(YEAR FROM timestamp) = :year
                  AND EXTRACT(MONTH FROM timestamp) = :month
            """),
            {"year": now.year, "month": now.month},
        )
        row = result.fetchone()
        return float(row[0]) if row and row[0] else 0.0

    async def get_status(self, db: AsyncSession) -> dict[str, Any]:
        """Get current budget status.

        Returns:
            Dict with mode, spent, remaining, ratio, message.
        """
        spent = await self.get_monthly_spending(db)
        remaining = max(0.0, self.monthly_budget - spent)
        ratio = spent / self.monthly_budget if self.monthly_budget > 0 else 0.0

        if ratio >= 1.0:
            mode = "local_only"
            message = "Monthly budget exhausted. Local-only mode active."
        elif ratio >= 0.90:
            mode = "minimal_cloud"
            message = f"Budget at 90%+. Cloud usage minimized. ${remaining:.2f} remaining."
        elif ratio >= 0.80:
            mode = "reduced_cloud"
            message = f"Budget at 80%+. Expensive models restricted. ${remaining:.2f} remaining."
        else:
            mode = "normal"
            message = f"Normal mode. ${remaining:.2f} remaining of ${self.monthly_budget:.2f} budget."

        return {
            "mode": mode,
            "spent": round(spent, 4),
            "remaining": round(remaining, 4),
            "ratio": round(ratio, 4),
            "message": message,
        }

    async def log_usage(
        self,
        db: AsyncSession,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float,
        reason: str,
        asset: str | None = None,
        task: str | None = None,
    ) -> None:
        """Log an API usage entry.

        Every AI API call must be logged here for cost tracking.
        """
        await db.execute(
            text("""
                INSERT INTO api_usage
                    (provider, model, input_tokens, output_tokens,
                     estimated_cost, reason, asset, task)
                VALUES
                    (:provider, :model, :input_tokens, :output_tokens,
                     :cost, :reason, :asset, :task)
            """),
            {
                "provider": provider,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": estimated_cost,
                "reason": reason,
                "asset": asset,
                "task": task,
            },
        )
        await db.commit()

        logger.info(
            "api_usage_logged",
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=estimated_cost,
            reason=reason,
            asset=asset,
        )
