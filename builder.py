# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml",
#     "typer",
#     "jinja2",
#     "pydantic",
#     "rich",
# ]
# ///
import shutil
import subprocess
import tempfile
import yaml
import typer
from pydantic import BaseModel
from pathlib import Path
import jinja2
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TaskProgressColumn,
)

app = typer.Typer()
console = Console()


def url(path: Path) -> str:
    assert isinstance(path, Path)
    return f"[{path.name}]({path.as_posix()})"


template_text = r"""
Список заданий для CTF:

| Название | Описание | Данные файлы | Решение | Флаг |
| -------- | -------- | -------- | -------- | -------- |
{% for task in tasks %}| {{ task.name }} | {{ (task.build.parent / "task.md") | url }} | {% for i in task.give %}{{ i | url }}{% if not loop.last %}, {% endif %}{% endfor %} | {{ (task.build.parent / "writeup.md") | url }} | {{ task.flag }} |
{% endfor %}
"""


class Task(BaseModel):
    name: str
    flag: str
    build: Path
    give: list[Path]

class Config(BaseModel):
    participant_data: Path
    global_info: Path


class GlobalConfig(BaseModel):
    config: Config
    tasks: list[Task]


def load_config(file_path: str) -> GlobalConfig:
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)
    return GlobalConfig.model_validate(config)


def build_task(task: Task, temp_dir: Path) -> None:
    temp_dir.mkdir(parents=True, exist_ok=True)
    compose_file = Path(task.build)
    if not compose_file.exists():
        raise FileNotFoundError(f"Compose file not found: {compose_file}")

    result = subprocess.Popen(
        [
            "docker-compose", 
            "-f", compose_file.name, 
            "build",
        ],
        cwd=compose_file.parent,
        env={
            "DOCKER_BUILDKIT": "0",
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).wait(30)
    assert result == 0, f"Failed to build task: {task.name}"

    result = subprocess.Popen(
        [
            "docker-compose", 
            "-f", compose_file.name, 
            "run", "--rm",
            "--remove-orphans",
            "app",
        ],
        cwd=compose_file.parent,
        env={
            "FLAG": task.flag,
            "DOCKER_BUILDKIT": "0",
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).wait(30)
    assert result == 0, f"Failed to run task: {task.name}"
    task_description = compose_file.parent / "task.md"
    assert task_description.exists(), f"Task description not found: {task_description}"
    shutil.copy(task_description, temp_dir / "task.md")
    for give in task.give:
        assert give.exists() and give.is_file(), f"Give file not found: {give}"
        shutil.copy(give, temp_dir / give.name)


@app.command()
def main(builder_config: str = "builder-config.yaml"):
    config = load_config(builder_config)

    temp_dir = Path(tempfile.mkdtemp())
    console.print(f"[bold]Temp dir:[/] {temp_dir}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        progress_task = progress.add_task(
            "[cyan]Обработка тасков...", total=len(config.tasks)
        )

        for task in config.tasks:
            progress.update(progress_task, description=f"[cyan]Таск: {task.name}")
            task_dir = temp_dir / task.name
            build_task(task, task_dir)
            progress.advance(progress_task)


    environment = jinja2.Environment(autoescape=False)
    environment.filters["url"] = url
    template = environment.from_string(template_text)
    with config.config.global_info.open("w", encoding="utf-8") as f:
        f.write(template.render(tasks=config.tasks))

    target = config.config.participant_data.stem
    extension = config.config.participant_data.suffix.removeprefix(".")
    shutil.make_archive(target, extension, temp_dir)
    console.print(f"[bold green]Done:[/] participant data -> {config.config.participant_data}")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    app()
