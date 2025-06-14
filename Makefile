# Ethics-by-Design Framework Makefile
# ====================================
# 
# Comprehensive build and test automation for the ethics-by-design framework
# Supports development, testing, experimentation, and deployment workflows

.PHONY: help install install-dev test test-coverage lint format clean \
        experiments run-all-experiments performance-test \
        generate-report generate-visualizations \
        docker-build docker-run setup-env \
        benchmark profile docs

# Default target
help:
	@echo "Ethics-by-Design Framework - Available Commands"
	@echo "================================================"
	@echo ""
	@echo "🚀 Setup & Installation:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make setup-env        Setup complete development environment"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test             Run all tests"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo "  make lint             Run code linting (flake8, black)"
	@echo "  make format           Format code with black"
	@echo ""
	@echo "🔬 Experiments & Analysis:"
	@echo "  make experiments      Run all experiments"
	@echo "  make performance-test Run performance evaluation"
	@echo "  make benchmark        Run comprehensive benchmarks"
	@echo "  make profile          Profile system performance"
	@echo ""
	@echo "📊 Reports & Visualization:"
	@echo "  make generate-report  Generate comprehensive paper report"
	@echo "  make generate-viz     Generate all visualizations"
	@echo "  make docs             Generate documentation"
	@echo ""
	@echo "🐳 Docker & Deployment:"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run in Docker container"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean            Clean temporary files and caches"
	@echo "  make clean-all        Deep clean including results"

# ===========================
# SETUP & INSTALLATION
# ===========================

install:
	@echo "📦 Installing production dependencies..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ Production installation complete!"

install-dev: install
	@echo "🛠️  Installing development dependencies..."
	pip install pytest pytest-cov black flake8 mypy
	pip install matplotlib seaborn plotly jupyter
	pip install scipy scikit-learn pandas
	@echo "✅ Development installation complete!"

setup-env: install-dev
	@echo "🌍 Setting up complete development environment..."
	mkdir -p results/figures results/data results/logs
	mkdir -p logs
	@echo "✅ Environment setup complete!"

# ===========================
# TESTING & QUALITY ASSURANCE
# ===========================

test:
	@echo "🧪 Running test suite..."
	python -m pytest tests/ -v --tb=short
	@echo "✅ All tests passed!"

test-coverage:
	@echo "📊 Running tests with coverage analysis..."
	python -m pytest tests/ --cov=ethics_framework --cov-report=html --cov-report=term
	@echo "📈 Coverage report generated in htmlcov/"

lint:
	@echo "🔍 Running code quality checks..."
	flake8 ethics_framework/ experiments/ tests/ --max-line-length=100 --ignore=E203,W503
	black --check ethics_framework/ experiments/ tests/
	@echo "✅ Code quality checks passed!"

format:
	@echo "🎨 Formatting code with black..."
	black ethics_framework/ experiments/ tests/
	@echo "✅ Code formatting complete!"

# ===========================
# EXPERIMENTS & ANALYSIS
# ===========================

experiments: setup-env
	@echo "🔬 Running all experiments..."
	python experiments/run_all_experiments.py
	@echo "✅ All experiments completed!"

performance-test:
	@echo "⚡ Running performance evaluation..."
	python experiments/performance_evaluation.py
	@echo "✅ Performance evaluation complete!"

baseline-comparison:
	@echo "📊 Running baseline comparison..."
	python experiments/baseline_comparison.py
	@echo "✅ Baseline comparison complete!"

scalability-test:
	@echo "📏 Running scalability analysis..."
	python experiments/scalability_analysis.py
	@echo "✅ Scalability analysis complete!"

constraint-composition:
	@echo "🔗 Running constraint composition study..."
	python experiments/constraint_composition_study.py
	@echo "✅ Constraint composition study complete!"

benchmark: setup-env
	@echo "🏃 Running comprehensive benchmarks..."
	python experiments/performance_evaluation.py --benchmark
	python experiments/scalability_analysis.py --benchmark
	@echo "✅ Benchmarking complete!"

profile:
	@echo "🔍 Profiling system performance..."
	python -m cProfile -o profile_results.prof experiments/performance_evaluation.py
	python -c "import pstats; p = pstats.Stats('profile_results.prof'); p.sort_stats('cumulative').print_stats(20)"
	@echo "✅ Profiling complete!"

# ===========================
# REPORTS & VISUALIZATION
# ===========================

generate-report: experiments
	@echo "📄 Generating comprehensive paper report..."
	python generate_paper_report.py
	@echo "✅ Paper report generated!"

generate-viz:
	@echo "📊 Generating visualizations..."
	python -c "from ethics_framework.visualization import *; generate_all_plots()"
	@echo "✅ Visualizations generated!"

docs:
	@echo "📚 Generating documentation..."
	@echo "Documentation generation not yet implemented"
	@echo "⚠️  TODO: Add Sphinx documentation generation"

# ===========================
# DOCKER & DEPLOYMENT
# ===========================

docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t ethics-framework:latest .
	@echo "✅ Docker image built!"

docker-run: docker-build
	@echo "🚀 Running in Docker container..."
	docker run -it --rm -v $(PWD)/results:/app/results ethics-framework:latest
	@echo "✅ Docker run complete!"

# ===========================
# MAINTENANCE & CLEANUP
# ===========================

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -f profile_results.prof
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "✅ Cleanup complete!"

clean-all: clean
	@echo "🧹 Deep cleaning all generated files..."
	rm -rf results/
	rm -rf logs/
	rm -f *.json
	rm -f *.log
	rm -f *.prof
	@echo "✅ Deep cleanup complete!"

# ===========================
# DEVELOPMENT WORKFLOWS
# ===========================

dev-setup: setup-env format lint test
	@echo "🚀 Development environment ready!"

ci-test: install test lint
	@echo "✅ CI pipeline tests passed!"

quick-test:
	@echo "⚡ Running quick tests..."
	python -m pytest tests/ -x --tb=short
	@echo "✅ Quick tests passed!"

# ===========================
# RESEARCH WORKFLOWS
# ===========================

paper-ready: clean experiments generate-report generate-viz
	@echo "📄 Generating paper-ready results..."
	@echo "✅ All paper materials generated!"

reproduce-results: clean-all setup-env experiments
	@echo "🔄 Reproducing all experimental results..."
	@echo "✅ Results reproduction complete!"

# ===========================
# UTILITY TARGETS
# ===========================

check-deps:
	@echo "🔍 Checking dependencies..."
	pip check
	@echo "✅ Dependencies are consistent!"

list-experiments:
	@echo "🔬 Available experiments:"
	@echo "  • performance_evaluation.py - Performance overhead analysis"
	@echo "  • baseline_comparison.py - Baseline vs ethics-aware comparison"
	@echo "  • scalability_analysis.py - System scalability evaluation"
	@echo "  • constraint_composition_study.py - Constraint interaction analysis"
	@echo "  • run_all_experiments.py - Comprehensive experiment suite"

show-results:
	@echo "📊 Recent results:"
	@ls -la results/ 2>/dev/null || echo "No results directory found. Run 'make experiments' first."

# ===========================
# CONFIGURATION
# ===========================

# Python interpreter
PYTHON := python3

# Test configuration
TEST_ARGS := -v --tb=short

# Coverage configuration
COV_ARGS := --cov=ethics_framework --cov-report=html --cov-report=term-missing

# Linting configuration
LINT_DIRS := ethics_framework experiments tests
MAX_LINE_LENGTH := 100

# Docker configuration
DOCKER_IMAGE := ethics-framework
DOCKER_TAG := latest 