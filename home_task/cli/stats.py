import typer
import uuid
import numpy as np
from collections import defaultdict

from home_task.db import get_session
from home_task.models import JobPosting, DaysToHireStatistic

app = typer.Typer(help="CLI tool with subcommands")
stat_app = typer.Typer(help="Commands for statistics")
app.add_typer(stat_app, name="stats")


def compute_statistics(days_to_hire_list: list[int], min_required: int):
    if len(days_to_hire_list) < min_required:
        return None

    array = np.array(days_to_hire_list)
    lower = np.percentile(array, 10)
    upper = np.percentile(array, 90)
    filtered = array[(array >= lower) & (array <= upper)]

    if len(filtered) < min_required:
        return None

    return {
        "average": float(np.mean(filtered)),
        "minimum": float(np.min(filtered)),
        "maximum": float(np.max(filtered)),
        "count": int(len(filtered)),
    }


def add_statistic_row(result_rows, country_code, standard_job_id, stats):
    result_rows.append(DaysToHireStatistic(
        id=str(uuid.uuid4()),
        country_code=country_code,
        standard_job_id=standard_job_id,
        average_days_to_hire=round(float(stats["average"]), 1),
        min_days_to_hire=round(float(stats["minimum"]), 1),
        max_days_to_hire=round(float(stats["maximum"]), 1),
        num_postings=stats["count"]
    ))


@stat_app.command("store")
def store_days_to_hire_stat(
    min_required: int = typer.Option(5, help="Minimum number of job postings for a valid stat")
):
    with get_session() as session:
        try:
            postings = session.query(JobPosting).filter(JobPosting.days_to_hire != None).yield_per(1000)

            stats_per_group = defaultdict(list)
            world_stats = defaultdict(list)

            for post in postings:
                if post.country_code is None:
                    world_stats[post.standard_job_id].append(post.days_to_hire)
                else:
                    stats_per_group[(post.country_code, post.standard_job_id)].append(post.days_to_hire)

            result_rows = []

            for (country, standard_job_id), values in stats_per_group.items():
                stats = compute_statistics(values, min_required)
                if stats:
                    add_statistic_row(result_rows, country, standard_job_id, stats)

            for standard_job_id, values in world_stats.items():
                stats = compute_statistics(values, min_required)
                if stats:
                    add_statistic_row(result_rows, None, standard_job_id, stats)

            session.query(DaysToHireStatistic).delete()
            session.add_all(result_rows)
            session.commit()

            typer.echo(f"Stored {len(result_rows)} rows of statistics")
        except Exception as e:
            session.rollback()
            typer.echo(f"Error occurred: {e}", err=True)
            raise


if __name__ == "__main__":
    app()
