"""Main orchestration script for building and serving IngredientIQ."""

import argparse
import logging
import sys
from pathlib import Path

from pipeline.build_reference_db import main as build_reference_db
from pipeline.train_pipeline import main as train_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ingredientiq_pipeline.log"),
    ],
)
logger = logging.getLogger(__name__)


def setup_project_directories(project_dir: Path) -> dict:
    """
    Ensure all required project directories exist.

    Args:
        project_dir: Root project directory

    Returns:
        Dictionary mapping directory names to paths
    """
    logger.info("Setting up project directories...")

    directories = {
        "data": project_dir / "data",
        "data_raw": project_dir / "data" / "raw",
        "data_processed": project_dir / "data" / "processed",
        "data_reference": project_dir / "data" / "reference",
        "models": project_dir / "models",
        "logs": project_dir / "logs",
    }

    for dir_name, dir_path in directories.items():
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"  ✓ {dir_path}")

    return directories


def run_build_pipeline(project_dir: Path) -> bool:
    """
    Run reference database build pipeline.

    Args:
        project_dir: Root project directory

    Returns:
        True if successful
    """
    logger.info("\n" + "=" * 70)
    logger.info("STEP 1: BUILDING REFERENCE DATABASES")
    logger.info("=" * 70)

    try:
        build_reference_db(project_dir / "data")
        logger.info("✅ Reference databases built successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Reference database build failed: {e}", exc_info=True)
        return False


def run_training_pipeline(project_dir: Path) -> bool:
    """
    Run model training pipeline.

    Args:
        project_dir: Root project directory

    Returns:
        True if successful
    """
    logger.info("\n" + "=" * 70)
    logger.info("STEP 2: TRAINING ML MODELS")
    logger.info("=" * 70)

    try:
        summary = train_pipeline(project_dir)
        if summary.get("status") == "completed":
            logger.info("✅ Model training completed successfully")
            return True
        else:
            logger.error("❌ Model training failed")
            return False
    except Exception as e:
        logger.error(f"❌ Training pipeline failed: {e}", exc_info=True)
        return False


def verify_models(project_dir: Path) -> bool:
    """
    Verify all required model files exist.

    Args:
        project_dir: Root project directory

    Returns:
        True if all required files are present
    """
    logger.info("\n" + "=" * 70)
    logger.info("STEP 3: VERIFYING MODEL FILES")
    logger.info("=" * 70)

    required_files = [
        project_dir / "models" / "safety_classifier.pkl",
        project_dir / "data" / "reference" / "ingredient_safety.parquet",
        project_dir / "data" / "reference" / "inci_synonyms.parquet",
    ]

    all_exist = True
    for file_path in required_files:
        if file_path.exists():
            logger.info(f"  ✅ {file_path.relative_to(project_dir)}")
        else:
            logger.warning(f"  ⚠️  {file_path.relative_to(project_dir)} (will be created on startup)")
            all_exist = False

    return all_exist


def start_api_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Start FastAPI server.

    Args:
        host: Server host
        port: Server port
    """
    logger.info("\n" + "=" * 70)
    logger.info("STEP 4: STARTING API SERVER")
    logger.info("=" * 70)

    try:
        import uvicorn

        logger.info(f"Starting API server on {host}:{port}")
        logger.info("Press Ctrl+C to stop server")
        logger.info("Documentation: http://localhost:8000/docs")

        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=False,
            workers=4,
        )
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Failed to start API server: {e}", exc_info=True)
        sys.exit(1)


def main():
    """
    Main orchestration function.

    Parses command-line arguments and executes appropriate pipeline steps.
    """
    parser = argparse.ArgumentParser(
        description="IngredientIQ Pipeline - Build & Deploy"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start API server after building pipeline",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)",
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip model training (use existing models)",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("./"),
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()

    logger.info("=" * 70)
    logger.info("INGREDIENTIQ PIPELINE ORCHESTRATION")
    logger.info("=" * 70)
    logger.info(f"Project directory: {project_dir}")

    # Step 1: Setup directories
    try:
        setup_project_directories(project_dir)
    except Exception as e:
        logger.error(f"Directory setup failed: {e}")
        sys.exit(1)

    # Step 2: Build reference database
    if not run_build_pipeline(project_dir):
        logger.error("Pipeline aborted: Reference database build failed")
        sys.exit(1)

    # Step 3: Train models (skip if --skip-training)
    if not args.skip_training:
        if not run_training_pipeline(project_dir):
            logger.error("Pipeline aborted: Model training failed")
            sys.exit(1)
    else:
        logger.info("Skipping model training (--skip-training)")

    # Step 4: Verify models
    all_models_present = verify_models(project_dir)
    if not all_models_present:
        logger.warning("Some model files missing - they will be created on first use")

    # Step 5: Start server if requested
    if args.serve:
        start_api_server(host=args.host, port=args.port)
    else:
        logger.info("\n" + "=" * 70)
        logger.info("PIPELINE COMPLETE ✅")
        logger.info("=" * 70)
        logger.info("\nTo start the API server, run:")
        logger.info(f"  python run_pipeline.py --serve")
        logger.info(f"\nOr with custom host/port:")
        logger.info(f"  python run_pipeline.py --serve --host 0.0.0.0 --port 8000")
        logger.info("\nDocumentation will be available at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
