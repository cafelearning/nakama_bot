from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


# Function to build the admin keyboard
def admin_inline_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('File Upload', callback_data='save_file'),
            InlineKeyboardButton('File Download', callback_data='get_file'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def user_inline_keyboard():
    keyboard = [
        ["List Files", "Get File by Name"],
        ["Get File by ID"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def master_inline_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('Add New Admin...', callback_data='add_new_admin'),
            InlineKeyboardButton('Admin List', callback_data='admin_list'),
        ],
        [
            InlineKeyboardButton('File Upload', callback_data='save_file'),
            InlineKeyboardButton('File Download', callback_data='get_file'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

