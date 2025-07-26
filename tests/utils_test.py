import pytest
import asyncio
from link_parser import extract_metadata

@pytest.mark.asyncio
@pytest.mark.parametrize("url, expected_in_title", [
    ("https://github.com/haoheliu/versatile_audio_super_resolution", "GitHub Repo"),
    ("https://youtu.be/IQ5k4qSBFwg", "YouTube"),
    ("https://arxiv.org/abs/2106.01354", "ArXiv"),
    ("https://habr.com/ru/articles/123456/", "Habr"),
    ("https://medium.com/some-article", "Без названия"),
    ("https://example.com", "Ссылка с example.com"),
])
async def test_extract_metadata(url, expected_in_title):
    title, summary = await extract_metadata(url)
    assert expected_in_title in title
