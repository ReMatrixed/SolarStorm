from aiogram import types

# Пресет клавиатуры для ответ на вопрос о рекомендуемых данных
kb_optional_data_buttons = [
    [
        types.InlineKeyboardButton(text="Да ✅", callback_data="statistics_allow"),
        types.InlineKeyboardButton(text="Нет ❌", callback_data="statistics_disallow")
    ]
]
kb_optional_data = types.InlineKeyboardMarkup(inline_keyboard = kb_optional_data_buttons)

# Пресет клавиатуры для ответ на вопрос о выборе предметы
kb_subject_selection_buttons = [
    [
        types.InlineKeyboardButton(text = "📐 Математика", callback_data = "subject_maths"),
        types.InlineKeyboardButton(text = "✒️ Русский язык", callback_data = "subject_russian")
    ],
    [
        types.InlineKeyboardButton(text = "🖥️ Информатика", callback_data = "subject_informatics"),
        types.InlineKeyboardButton(text = "💡 Физика", callback_data = "subject_physics")
    ],
    [
        types.InlineKeyboardButton(text = "🌍 География", callback_data = "subject_geography"),
        types.InlineKeyboardButton(text = "📜 История", callback_data = "subject_history")
    ],
    [
        types.InlineKeyboardButton(text = "🧪 Химия", callback_data = "subject_chemistry"),
        types.InlineKeyboardButton(text = "🌱 Биология", callback_data = "subject_biology")
    ],
    [
        types.InlineKeyboardButton(text = "🎩 Английский язык", callback_data = "subject_english")
    ],
    [
        types.InlineKeyboardButton(text = "💼 Обществознание", callback_data = "subject_social")
    ]
]
kb_subject_selection = types.InlineKeyboardMarkup(inline_keyboard = kb_subject_selection_buttons)