"""Tests for Docker and deployment configuration."""

import pytest
import yaml
import json
from pathlib import Path


def test_docker_compose_structure():
    """Test docker-compose.yml has required structure."""
    compose_path = Path(__file__).parent.parent.parent / "docker-compose.yml"
    
    with open(compose_path) as f:
        compose = yaml.safe_load(f)
    
    # Check required services
    assert "services" in compose
    assert "backend" in compose["services"]
    assert "frontend" in compose["services"]
    
    # Check health checks
    assert "healthcheck" in compose["services"]["backend"]
    assert "healthcheck" in compose["services"]["frontend"]
    
    # Check networks
    assert "networks" in compose
    assert "delta-network" in compose["networks"]


def test_package_json_scripts():
    """Test package.json has required scripts."""
    package_path = Path(__file__).parent.parent.parent / "package.json"
    
    with open(package_path) as f:
        package = json.load(f)
    
    # Check required scripts
    required_scripts = ["dev", "build", "test"]
    for script in required_scripts:
        assert script in package["scripts"]
    
    # Check workspaces include both frontend and backend
    assert "workspaces" in package
    assert "frontend" in package["workspaces"]
    assert "backend" in package["workspaces"]


def test_requirements_no_duplicates():
    """Test requirements.txt has no duplicate packages."""
    req_path = Path(__file__).parent.parent / "requirements.txt"
    
    with open(req_path) as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    # Extract package names (before == or >= operators)
    packages = []
    for line in lines:
        if "==" in line:
            package = line.split("==")[0]
        elif ">=" in line:
            package = line.split(">=")[0]
        else:
            package = line
        packages.append(package.lower())
    
    # Check for duplicates
    duplicates = [pkg for pkg in set(packages) if packages.count(pkg) > 1]
    assert len(duplicates) == 0, f"Duplicate packages found: {duplicates}"
