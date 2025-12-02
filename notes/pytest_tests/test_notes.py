import pytest

from notes.models import Note


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_note_exists(note, name):
    notes_count = Note.objects.count()
    # Общее количество заметок в БД равно 1.
    assert notes_count == 1
    # Заголовок объекта, полученного при помощи фикстуры note,
    # совпадает с тем, что указан в фикстуре.
    assert note.title == 'Заголовок'


# Обозначаем, что тесту нужен доступ к БД.
# Без этой метки тест выдаст ошибку доступа к БД.
@pytest.mark.django_db
def test_empty_db():
    notes_count = Note.objects.count()
    # В пустой БД никаких заметок не будет:
    assert notes_count == 0


@pytest.mark.parametrize("attr, expected", [
    ("title", "Заголовок"),
    ("text",  "Текст заметки"),
    ("slug",  "note-slug"),
])
def test_note_string_fields(note, attr, expected):
    assert getattr(note, attr) == expected

def test_note_author(note, author):
    # автора удобнее проверить отдельным тестом,
    # потому что expected — это объект-фикстура
    assert note.author == author