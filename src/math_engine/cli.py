"""
Mega HSSE Transformer — Command-Line Interface

Provides command-line access to all mathematical safety engine calculations
with explicit input and output display.

Usage:
    python -m src.math_engine.cli <command> [options]

Commands:
    risk        Fine-Kinney risk calculation
    exposure    Time-Weighted Average (TWA) exposure
    lifting     Lifting safety factor
    incident    Combined failure probability
    verify      Deterministic verification check
    train       Open training artifact build from dataset folders
    evaluate    Benchmark evaluation report generation

Run `python -m src.math_engine.cli --help` for full usage.

Research Status: Foundation Built — Validation Pending
"""

import argparse
import json
import sys


def _print_result(label: str, result: object) -> None:
    """Print a calculation result as formatted JSON."""
    data = {k: v for k, v in vars(result).items()}
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    print(json.dumps(data, indent=2))
    print(f"{'=' * 60}\n")


def cmd_risk(args: argparse.Namespace) -> None:
    """Run Fine-Kinney risk calculation from CLI arguments."""
    from src.math_engine.schemas import RiskInput
    from src.math_engine.risk import assess_risk

    inputs = RiskInput(
        probability=args.probability,
        severity=args.severity,
        exposure=args.exposure,
        control_efficiency=args.control_efficiency,
    )
    result = assess_risk(inputs)
    _print_result("Fine-Kinney Risk Assessment", result)


def cmd_exposure(args: argparse.Namespace) -> None:
    """Run TWA exposure calculation from CLI arguments."""
    from src.math_engine.schemas import ExposureInput
    from src.math_engine.exposure import calculate_twa

    concentrations = [float(c) for c in args.concentrations.split(",")]
    durations = [float(t) for t in args.durations.split(",")]

    inputs = ExposureInput(concentrations=concentrations, durations=durations)
    result = calculate_twa(inputs)
    _print_result("TWA Exposure Calculation", result)


def cmd_lifting(args: argparse.Namespace) -> None:
    """Run lifting safety factor calculation from CLI arguments."""
    from src.math_engine.schemas import LiftingInput
    from src.math_engine.lifting import calculate_safety_factor

    inputs = LiftingInput(
        breaking_strength=args.breaking_strength,
        applied_load=args.applied_load,
        dynamic_factor=args.dynamic_factor,
        minimum_sf=args.minimum_sf,
    )
    result = calculate_safety_factor(inputs)
    _print_result("Lifting Safety Factor", result)


def cmd_incident(args: argparse.Namespace) -> None:
    """Run failure probability calculation from CLI arguments."""
    from src.math_engine.schemas import IncidentInput
    from src.math_engine.incident import calculate_failure_probability

    probabilities = [float(p) for p in args.probabilities.split(",")]

    inputs = IncidentInput(probabilities=probabilities, threshold=args.threshold)
    result = calculate_failure_probability(inputs)
    _print_result("Failure Probability (RCA)", result)


def cmd_verify(args: argparse.Namespace) -> None:
    """Run deterministic verification check from CLI arguments."""
    from src.verification.engine import apply_rules

    context = {}
    if args.oxygen_percent is not None:
        context["oxygen_percent"] = args.oxygen_percent
    if args.safety_factor is not None:
        context["safety_factor"] = args.safety_factor
    if args.twa_value is not None and args.twa_oel is not None:
        context["twa_value"] = args.twa_value
        context["twa_oel"] = args.twa_oel
    if args.risk_score is not None:
        context["risk_score"] = args.risk_score

    results = apply_rules(context)

    print(f"\n{'=' * 60}")
    print("  Deterministic Verification Results")
    print(f"{'=' * 60}")
    print(json.dumps(results, indent=2))
    print(f"{'=' * 60}\n")


def cmd_train(args: argparse.Namespace) -> None:
    """Run open training flow and save model artifact."""
    from src.hsse_transformer.open_framework import train_open_framework

    result = train_open_framework(args.dataset_root, args.output)
    print(f"\n{'=' * 60}")
    print("  Open Training Artifact")
    print(f"{'=' * 60}")
    print(json.dumps(result, indent=2))
    print(f"{'=' * 60}\n")


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Run benchmark evaluation flow and save report."""
    from src.hsse_transformer.open_framework import run_benchmark_evaluation

    result = run_benchmark_evaluation(args.dataset_root, args.output)
    print(f"\n{'=' * 60}")
    print("  Benchmark Evaluation Report")
    print(f"{'=' * 60}")
    print(json.dumps(result, indent=2))
    print(f"{'=' * 60}\n")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m src.math_engine.cli",
        description="Mega HSSE Transformer — Mathematical Safety Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m src.math_engine.cli risk "
            "--probability 6 --severity 15 --exposure 3 --control-efficiency 0.8\n"
            "  python -m src.math_engine.cli exposure "
            "--concentrations 50,30 --durations 4,4\n"
            "  python -m src.math_engine.cli lifting "
            "--breaking-strength 250 --applied-load 50 --dynamic-factor 1.5\n"
            "  python -m src.math_engine.cli incident "
            "--probabilities 0.1,0.05,0.02 --threshold 0.1\n"
            "  python -m src.math_engine.cli verify --oxygen-percent 18.0\n"
            "  python -m src.math_engine.cli train --dataset-root ./dataset "
            "--output ./artifacts/open_model.json\n"
            "  python -m src.math_engine.cli evaluate --dataset-root ./dataset "
            "--output ./artifacts/benchmark_report.json\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -----------------------------------------------------------------------
    # risk subcommand
    # -----------------------------------------------------------------------
    risk_parser = subparsers.add_parser(
        "risk",
        help="Fine-Kinney risk calculation (Ri = P × S × E)",
    )
    risk_parser.add_argument(
        "--probability", "-p", type=float, required=True,
        help="Probability of hazard occurrence (Fine-Kinney scale, e.g., 0.1–10)",
    )
    risk_parser.add_argument(
        "--severity", "-s", type=float, required=True,
        help="Consequence severity (Fine-Kinney scale, e.g., 1–40)",
    )
    risk_parser.add_argument(
        "--exposure", "-e", type=float, required=True,
        help="Exposure frequency (Fine-Kinney scale, e.g., 0.5–10)",
    )
    risk_parser.add_argument(
        "--control-efficiency", type=float, default=0.0,
        help="Control efficiency factor ε (0.0–1.0, default: 0.0)",
    )
    risk_parser.set_defaults(func=cmd_risk)

    # -----------------------------------------------------------------------
    # exposure subcommand
    # -----------------------------------------------------------------------
    exp_parser = subparsers.add_parser(
        "exposure",
        help="Time-Weighted Average (TWA) exposure calculation",
    )
    exp_parser.add_argument(
        "--concentrations", "-c", required=True,
        help="Comma-separated hazard concentrations, e.g., '50,30'",
    )
    exp_parser.add_argument(
        "--durations", "-d", required=True,
        help="Comma-separated exposure durations in hours, e.g., '4,4'",
    )
    exp_parser.set_defaults(func=cmd_exposure)

    # -----------------------------------------------------------------------
    # lifting subcommand
    # -----------------------------------------------------------------------
    lift_parser = subparsers.add_parser(
        "lifting",
        help="Lifting safety factor calculation",
    )
    lift_parser.add_argument(
        "--breaking-strength", type=float, required=True,
        help="Rated breaking strength of lifting equipment",
    )
    lift_parser.add_argument(
        "--applied-load", type=float, required=True,
        help="Actual weight of the load to be lifted",
    )
    lift_parser.add_argument(
        "--dynamic-factor", type=float, required=True,
        help="Dynamic amplification factor (e.g., 1.5 for offshore)",
    )
    lift_parser.add_argument(
        "--minimum-sf", type=float, default=5.0,
        help="Minimum acceptable safety factor (default: 5.0 for critical lifts)",
    )
    lift_parser.set_defaults(func=cmd_lifting)

    # -----------------------------------------------------------------------
    # incident subcommand
    # -----------------------------------------------------------------------
    inc_parser = subparsers.add_parser(
        "incident",
        help="Combined failure probability (RCA / fault tree)",
    )
    inc_parser.add_argument(
        "--probabilities", required=True,
        help="Comma-separated individual failure probabilities, e.g., '0.1,0.05,0.02'",
    )
    inc_parser.add_argument(
        "--threshold", type=float, default=0.1,
        help="Maximum acceptable combined failure probability (default: 0.1)",
    )
    inc_parser.set_defaults(func=cmd_incident)

    # -----------------------------------------------------------------------
    # verify subcommand
    # -----------------------------------------------------------------------
    ver_parser = subparsers.add_parser(
        "verify",
        help="Deterministic verification check against safety rules",
    )
    ver_parser.add_argument(
        "--oxygen-percent", type=float, default=None,
        help="Oxygen concentration in percent (e.g., 18.0)",
    )
    ver_parser.add_argument(
        "--safety-factor", type=float, default=None,
        help="Computed safety factor for lifting check",
    )
    ver_parser.add_argument(
        "--twa-value", type=float, default=None,
        help="Computed TWA value for exposure check",
    )
    ver_parser.add_argument(
        "--twa-oel", type=float, default=None,
        help="Occupational exposure limit (OEL) for TWA comparison",
    )
    ver_parser.add_argument(
        "--risk-score", type=float, default=None,
        help="Risk score for extreme risk check",
    )
    ver_parser.set_defaults(func=cmd_verify)

    # -----------------------------------------------------------------------
    # train subcommand
    # -----------------------------------------------------------------------
    train_parser = subparsers.add_parser(
        "train",
        help="Build open training artifact from dataset folder structure",
    )
    train_parser.add_argument(
        "--dataset-root", required=True,
        help="Absolute or relative path to dataset root containing 01..04 folders",
    )
    train_parser.add_argument(
        "--output", required=True,
        help="Output JSON path for generated training artifact",
    )
    train_parser.set_defaults(func=cmd_train)

    # -----------------------------------------------------------------------
    # evaluate subcommand
    # -----------------------------------------------------------------------
    eval_parser = subparsers.add_parser(
        "evaluate",
        help="Run benchmark scoring and generate proof report",
    )
    eval_parser.add_argument(
        "--dataset-root", required=True,
        help="Absolute or relative path to dataset root containing 01..04 folders",
    )
    eval_parser.add_argument(
        "--output", required=True,
        help="Output JSON path for generated benchmark report",
    )
    eval_parser.set_defaults(func=cmd_evaluate)

    return parser


def main(argv=None):
    """Main entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        args.func(args)
    except ValueError as exc:
        print(f"\nInput Error: {exc}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"\nUnexpected error: {exc}\n", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
