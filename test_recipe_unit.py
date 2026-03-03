"""
Unit tests for conda recipe validation.

Tests validate that the conda recipe is properly structured before attempting to build.
Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
"""

import os
import yaml
import pytest


def get_recipe_path():
    """Get the path to the recipe directory."""
    # Tests are in toledo/, recipe is in ../recipe/
    test_dir = os.path.dirname(os.path.abspath(__file__))
    recipe_dir = os.path.join(os.path.dirname(test_dir), "recipe")
    return recipe_dir


def load_meta_yaml():
    """Load and parse the meta.yaml file."""
    recipe_path = get_recipe_path()
    meta_path = os.path.join(recipe_path, "meta.yaml")
    
    if not os.path.exists(meta_path):
        pytest.skip(f"meta.yaml not found at {meta_path}")
    
    with open(meta_path, 'r') as f:
        content = f.read()
    
    # Remove Jinja2 template syntax for basic validation
    # Replace {% set ... %} lines with empty strings
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith('{%') and line.strip().endswith('%}'):
            continue
        # Replace {{ name|lower }} with "toledo"
        line = line.replace('{{ name|lower }}', 'toledo')
        # Replace {{ name }} with "toledo"
        line = line.replace('{{ name }}', 'toledo')
        # Replace {{ version }} with "0.0.4.3"
        line = line.replace('{{ version }}', '0.0.4.3')
        cleaned_lines.append(line)
    
    cleaned_content = '\n'.join(cleaned_lines)
    
    try:
        data = yaml.safe_load(cleaned_content)
        return data
    except yaml.YAMLError as e:
        pytest.fail(f"YAML syntax error in meta.yaml: {e}")


class TestRecipeSyntax:
    """Test that meta.yaml has valid YAML syntax."""
    
    def test_meta_yaml_is_valid_yaml(self):
        """Validate that meta.yaml can be parsed as valid YAML."""
        data = load_meta_yaml()
        assert data is not None, "meta.yaml should parse to a non-None value"
        assert isinstance(data, dict), "meta.yaml should parse to a dictionary"


class TestRequiredFields:
    """Test that meta.yaml contains all required fields."""
    
    def test_package_section_exists(self):
        """Validate that package section exists."""
        data = load_meta_yaml()
        assert 'package' in data, "meta.yaml must contain 'package' section"
    
    def test_package_name_exists(self):
        """Validate that package name is specified (Requirement 2.2)."""
        data = load_meta_yaml()
        assert 'package' in data, "meta.yaml must contain 'package' section"
        assert 'name' in data['package'], "package section must contain 'name' field"
        assert data['package']['name'] == 'toledo', "package name should be 'toledo'"
    
    def test_package_version_exists(self):
        """Validate that package version is specified."""
        data = load_meta_yaml()
        assert 'package' in data, "meta.yaml must contain 'package' section"
        assert 'version' in data['package'], "package section must contain 'version' field"
        assert data['package']['version'], "version should not be empty"
    
    def test_source_section_exists(self):
        """Validate that source section exists (Requirement 2.4)."""
        data = load_meta_yaml()
        assert 'source' in data, "meta.yaml must contain 'source' section"
    
    def test_build_section_exists(self):
        """Validate that build section exists."""
        data = load_meta_yaml()
        assert 'build' in data, "meta.yaml must contain 'build' section"
    
    def test_requirements_section_exists(self):
        """Validate that requirements section exists (Requirement 2.3)."""
        data = load_meta_yaml()
        assert 'requirements' in data, "meta.yaml must contain 'requirements' section"
    
    def test_test_section_exists(self):
        """Validate that test section exists (Requirement 2.5)."""
        data = load_meta_yaml()
        assert 'test' in data, "meta.yaml must contain 'test' section"
    
    def test_about_section_exists(self):
        """Validate that about section exists."""
        data = load_meta_yaml()
        assert 'about' in data, "meta.yaml must contain 'about' section"
    
    def test_about_license_exists(self):
        """Validate that license is specified."""
        data = load_meta_yaml()
        assert 'about' in data, "meta.yaml must contain 'about' section"
        assert 'license' in data['about'], "about section must contain 'license' field"
        assert data['about']['license'], "license should not be empty"
    
    def test_about_license_file_exists(self):
        """Validate that license_file is specified."""
        data = load_meta_yaml()
        assert 'about' in data, "meta.yaml must contain 'about' section"
        assert 'license_file' in data['about'], "about section must contain 'license_file' field"
    
    def test_about_summary_exists(self):
        """Validate that summary is specified."""
        data = load_meta_yaml()
        assert 'about' in data, "meta.yaml must contain 'about' section"
        assert 'summary' in data['about'], "about section must contain 'summary' field"
        assert data['about']['summary'], "summary should not be empty"
    
    def test_about_home_exists(self):
        """Validate that home URL is specified."""
        data = load_meta_yaml()
        assert 'about' in data, "meta.yaml must contain 'about' section"
        assert 'home' in data['about'], "about section must contain 'home' field"


class TestDependencySpecifications:
    """Test that dependencies are properly specified (Requirement 2.3)."""
    
    def test_requirements_has_host_section(self):
        """Validate that requirements has host section."""
        data = load_meta_yaml()
        assert 'requirements' in data, "meta.yaml must contain 'requirements' section"
        assert 'host' in data['requirements'], "requirements must contain 'host' section"
    
    def test_requirements_has_run_section(self):
        """Validate that requirements has run section."""
        data = load_meta_yaml()
        assert 'requirements' in data, "meta.yaml must contain 'requirements' section"
        assert 'run' in data['requirements'], "requirements must contain 'run' section"
    
    def test_host_dependencies_include_python(self):
        """Validate that host dependencies include python."""
        data = load_meta_yaml()
        host_deps = data.get('requirements', {}).get('host', [])
        assert isinstance(host_deps, list), "host dependencies should be a list"
        assert 'python' in host_deps, "host dependencies must include 'python'"
    
    def test_host_dependencies_include_pip(self):
        """Validate that host dependencies include pip."""
        data = load_meta_yaml()
        host_deps = data.get('requirements', {}).get('host', [])
        assert 'pip' in host_deps, "host dependencies must include 'pip'"
    
    def test_host_dependencies_include_setuptools(self):
        """Validate that host dependencies include setuptools."""
        data = load_meta_yaml()
        host_deps = data.get('requirements', {}).get('host', [])
        assert 'setuptools' in host_deps, "host dependencies must include 'setuptools'"
    
    def test_run_dependencies_include_python(self):
        """Validate that run dependencies include python."""
        data = load_meta_yaml()
        run_deps = data.get('requirements', {}).get('run', [])
        assert isinstance(run_deps, list), "run dependencies should be a list"
        assert 'python' in run_deps, "run dependencies must include 'python'"
    
    def test_run_dependencies_include_pyserial(self):
        """Validate that run dependencies include pyserial (Requirement 2.3)."""
        data = load_meta_yaml()
        run_deps = data.get('requirements', {}).get('run', [])
        assert 'pyserial' in run_deps, "run dependencies must include 'pyserial'"


class TestEntryPoints:
    """Test that entry points are properly defined (Requirement 2.5)."""
    
    def test_build_has_entry_points(self):
        """Validate that build section has entry_points field."""
        data = load_meta_yaml()
        assert 'build' in data, "meta.yaml must contain 'build' section"
        assert 'entry_points' in data['build'], "build section must contain 'entry_points' field"
    
    def test_entry_points_is_list(self):
        """Validate that entry_points is a list."""
        data = load_meta_yaml()
        entry_points = data.get('build', {}).get('entry_points', [])
        assert isinstance(entry_points, list), "entry_points should be a list"
        assert len(entry_points) > 0, "entry_points should not be empty"
    
    def test_toledo_entry_point_exists(self):
        """Validate that toledo entry point is defined."""
        data = load_meta_yaml()
        entry_points = data.get('build', {}).get('entry_points', [])
        
        # Check if any entry point starts with "toledo"
        toledo_entry = None
        for ep in entry_points:
            if ep.startswith('toledo'):
                toledo_entry = ep
                break
        
        assert toledo_entry is not None, "entry_points must include 'toledo' command"
    
    def test_toledo_entry_point_format(self):
        """Validate that toledo entry point has correct format."""
        data = load_meta_yaml()
        entry_points = data.get('build', {}).get('entry_points', [])
        
        # Find toledo entry point
        toledo_entry = None
        for ep in entry_points:
            if ep.startswith('toledo'):
                toledo_entry = ep
                break
        
        assert toledo_entry is not None, "entry_points must include 'toledo' command"
        
        # Validate format: "toledo = toledo.cli:main"
        assert '=' in toledo_entry, "entry point should have format 'command = module:function'"
        parts = toledo_entry.split('=')
        assert len(parts) == 2, "entry point should have exactly one '=' separator"
        
        command = parts[0].strip()
        target = parts[1].strip()
        
        assert command == 'toledo', "entry point command should be 'toledo'"
        assert ':' in target, "entry point target should have format 'module:function'"
        
        module, function = target.split(':', 1)
        assert module == 'toledo.cli', "entry point should reference 'toledo.cli' module"
        assert function == 'main', "entry point should reference 'main' function"


class TestTestCommands:
    """Test that test commands are properly defined (Requirement 2.5)."""
    
    def test_test_has_imports(self):
        """Validate that test section has imports field."""
        data = load_meta_yaml()
        assert 'test' in data, "meta.yaml must contain 'test' section"
        assert 'imports' in data['test'], "test section should contain 'imports' field"
    
    def test_test_imports_include_toledo(self):
        """Validate that test imports include toledo module."""
        data = load_meta_yaml()
        imports = data.get('test', {}).get('imports', [])
        assert isinstance(imports, list), "test imports should be a list"
        assert 'toledo' in imports, "test imports must include 'toledo'"
    
    def test_test_has_commands(self):
        """Validate that test section has commands field (Requirement 2.5)."""
        data = load_meta_yaml()
        assert 'test' in data, "meta.yaml must contain 'test' section"
        assert 'commands' in data['test'], "test section should contain 'commands' field"
    
    def test_test_commands_is_list(self):
        """Validate that test commands is a list."""
        data = load_meta_yaml()
        commands = data.get('test', {}).get('commands', [])
        assert isinstance(commands, list), "test commands should be a list"
        assert len(commands) > 0, "test commands should not be empty"
    
    def test_test_commands_include_version(self):
        """Validate that test commands include version check."""
        data = load_meta_yaml()
        commands = data.get('test', {}).get('commands', [])
        
        # Check if any command tests --version
        has_version_test = any('--version' in cmd for cmd in commands)
        assert has_version_test, "test commands should include 'toledo --version'"
    
    def test_test_commands_include_help(self):
        """Validate that test commands include help check."""
        data = load_meta_yaml()
        commands = data.get('test', {}).get('commands', [])
        
        # Check if any command tests --help
        has_help_test = any('--help' in cmd for cmd in commands)
        assert has_help_test, "test commands should include 'toledo --help'"


class TestBuildScripts:
    """Test that build scripts exist."""
    
    def test_build_sh_exists(self):
        """Validate that build.sh exists for Unix platforms."""
        recipe_path = get_recipe_path()
        build_sh_path = os.path.join(recipe_path, "build.sh")
        assert os.path.exists(build_sh_path), "build.sh should exist in recipe directory"
    
    def test_bld_bat_exists(self):
        """Validate that bld.bat exists for Windows platform."""
        recipe_path = get_recipe_path()
        bld_bat_path = os.path.join(recipe_path, "bld.bat")
        assert os.path.exists(bld_bat_path), "bld.bat should exist in recipe directory"
