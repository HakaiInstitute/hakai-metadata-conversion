from hakai_metadata_conversion.__version__ import version
import tomllib

def load_pyproject():
    with open("pyproject.toml",'rb') as f:
        return tomllib.load(f)

def test_pyproject_version():
    pyproject = load_pyproject()
    assert pyproject, "Could not load pyproject.toml"
    assert "tool" in pyproject, "No 'tool' section in pyproject.toml"
    assert "poetry" in pyproject["tool"], "No 'poetry' section in pyproject.toml" 
    assert "version" in pyproject["tool"]["poetry"], "No 'version' in pyproject.toml"



def test_version():
    assert version

def test_version_match():
    pyproject = load_pyproject()
    assert version == pyproject["tool"]["poetry"]["version"]