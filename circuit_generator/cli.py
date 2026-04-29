"""CLI entry point: python -m circuit_generator <command>"""

from pathlib import Path

import click
import yaml

from .elements import ELEMENT_MAP, ELEMENT_NAMES_JA
from .nlp_converter import nl_to_svg, nl_to_yaml
from .renderer import circuit_to_svg, yaml_to_svg


@click.group()
def cli():
    """臨床工学技士国家試験 回路図SVG生成ツール"""


@cli.command()
@click.argument("yaml_file", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def render(yaml_file, output):
    """YAMLファイルからSVGを生成する"""
    yaml_to_svg(yaml_file, output)
    click.echo(f"SVG generated: {output}")


@cli.command()
@click.argument("description")
@click.option("--output", "-o", default="circuit.yaml", show_default=True)
def convert(description, output):
    """自然言語の回路記述をYAMLに変換する"""
    data = nl_to_yaml(description)
    Path(output).write_text(
        yaml.dump(data, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )
    click.echo(f"YAML generated: {output}")


@cli.command()
@click.argument("description")
@click.option("--output", "-o", default="circuit.svg", show_default=True)
@click.option("--yaml-out", "-y", default=None, help="中間YAMLも保存")
def generate(description, output, yaml_out):
    """自然言語の回路記述からSVGを直接生成する"""
    if yaml_out:
        data = nl_to_yaml(description)
        Path(yaml_out).write_text(
            yaml.dump(data, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
        circuit_to_svg(data, output)
        click.echo(f"YAML: {yaml_out}  SVG: {output}")
    else:
        nl_to_svg(description, output)
        click.echo(f"SVG generated: {output}")


@cli.command("list-elements")
def list_elements():
    """利用可能な回路素子の一覧を表示する"""
    click.echo("\n利用可能な素子タイプ一覧:\n")
    click.echo(f"{'type':<25} 日本語名")
    click.echo("-" * 50)
    for key in sorted(ELEMENT_MAP):
        click.echo(f"{key:<25} {ELEMENT_NAMES_JA.get(key, '')}")
    click.echo()


if __name__ == "__main__":
    cli()
