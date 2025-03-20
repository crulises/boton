import os
import pytest
import responses
from unittest.mock import patch, mock_open

from boton.interfaces.github_interface import GitHubInterface

# Este fixture también se puede definir en un archivo conftest.py en el directorio de tests.
# Se define acá para mantener todo en un solo archivo.
@pytest.fixture(scope="function")
@patch.dict(os.environ, {
    "GITHUB_TOKEN": "test_token", 
    "GITHUB_REPOSITORY": "test_owner/test_repo", 
    "GITHUB_EVENT_PATH": "test_event.json"
})
def github_interface():
    return GitHubInterface()

@patch("builtins.open", new_callable=mock_open, read_data='{"pull_request": {"number": 42}}')
def test_get_pr_number(mock_file, github_interface):
    """Testea la extracción del número de PR desde el evento de GitHub."""
    numero_pr = github_interface.get_pr_number()
    assert numero_pr == 42
    mock_file.assert_called_once_with("test_event.json", "r")

@responses.activate
def test_get_files_changed(github_interface):
    """
    Prueba la obtención de archivos modificados en un PR. Todo mockeado, no se hacen llamadas reales, 
    sin embargo, se describe la estructura esperada.
    """
    pr_number = 42
    files_url = f"https://api.github.com/repos/test_owner/test_repo/pulls/{pr_number}/files"
    responses.add(
        responses.GET,
        files_url,
        json=[{"filename": "file1.py"}, {"filename": "file2.py"}],
        status=200
    )

    files = github_interface.get_files_changed(pr_number)
    assert files == ["file1.py", "file2.py"]

@responses.activate
def test_get_file_diffs(github_interface):
    """
    Prueba la obtención del diff de un archivo en un PR. Todo mockeado, no se hacen llamadas reales,
    sin embargo, es la estructura que se espera obtener"""
    pr_number = 42
    files_url = f"https://api.github.com/repos/test_owner/test_repo/pulls/{pr_number}/files"
    responses.add(
        responses.GET,
        files_url,
        json=[{"filename": "file1.py", "patch": "diff --git a/file1.py b/file1.py\n+print('Hola')"}],
        status=200
    )

    diff = github_interface.get_file_diffs(pr_number, "file1.py")
    assert diff == "diff --git a/file1.py b/file1.py\n+print('Hola')"

@patch("builtins.open", new_callable=mock_open, read_data='{"pull_request": {"number": 42}}')
@responses.activate
def test_get_all_diffs(_, github_interface):
    """
    Prueba la obtención de todos los diffs de archivos en un PR. Todo mockeado, no se hacen llamadas reales,
    sin embargo, se describe la estructura esperada.
    """
    pr_number = 42
    files_url = f"https://api.github.com/repos/test_owner/test_repo/pulls/{pr_number}/files"
    responses.add(
        responses.GET,
        files_url,
        json=[
            {"filename": "file1.py", "patch": "diff --git a/file1.py b/file1.py\n+print('Hola')"},
            {"filename": "file2.py", "patch": "diff --git a/file2.py b/file2.py\n+print('Mundo')"}
        ],
        status=200
    )

    diffs = github_interface.get_all_diffs()
    expected_diffs = [
        "diff --git a/file1.py b/file1.py\n+print('Hola')",
        "diff --git a/file2.py b/file2.py\n+print('Mundo')"
    ]

    assert diffs == expected_diffs

@responses.activate
def test_comment_pr(github_interface):
    """
    Prueba la creación de un comentario en un PR. Todo mockeado, no se hacen llamadas reales,
    sin embargo, se verifica que se haya hecho exactamente una llamada a la API.
    """
    pr_number = 42
    comments_url = f"https://api.github.com/repos/test_owner/test_repo/pulls/{pr_number}/comments"
    responses.add(
        responses.POST,
        comments_url,
        json={},
        status=201
    )

    try:
        github_interface.comment_pr(pr_number, "This is a test comment")
        success = True
    except Exception:
        success = False

    assert success
    assert len(responses.calls) == 1  # Ensure exactly one API call was made