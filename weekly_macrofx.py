import asyncio
from macrofx import run_weekly_analysis

if __name__ == "__main__":
    result = asyncio.run(run_weekly_analysis(force=False))
    print(result)
