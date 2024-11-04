import asyncio
import os
from telegram.ext import (CommandHandler, MessageHandler, CallbackContext,
                          ApplicationBuilder, CallbackQueryHandler, ContextTypes,
                          filters)
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from db_settings import init_db, save_admin_to_db, get_admins, save_file_to_db, get_file_from_db
from keyboards import admin_inline_keyboard, master_inline_keyboard
from texts import *

load_dotenv()
TOKEN = os.getenv('TOKEN')
OWNER_ID = os.getenv('ADMIN')
CHANNEL_ID = os.getenv('CHANNEL')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == int(OWNER_ID):
        await update.message.reply_text(
            'Hello Master',
            reply_markup=master_inline_keyboard()
        )
        if context.args:
            await handle_url_message(update, context, context.args[0])
    elif user_id in get_admins():
        await update.message.reply_text(
            "Welcome, Admin! Please choose an option:",
            reply_markup=admin_inline_keyboard()
        )
    else:
        if context.args:
            await handle_url_message(update, context, context.args[0])
        else:
            await update.message.reply_text(user_welcome_message)
            await update.message.reply_text(user_welcome_message_fa)


async def add_new_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Enter New Admin ID: ")
    # Set a state to expect the next message as the new admin ID
    context.user_data['waiting_for_admin_id'] = True


async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    admins = get_admins()
    # markup = InlineKeyboardMarkup()
    keyboard = []
    for admin in admins:
        keyboard.append([
            InlineKeyboardButton(f'{admin}', callback_data=str(admin)),
            InlineKeyboardButton('\U0000274C', callback_data='nono')
        ])
        # markup.add(InlineKeyboardButton(text=admin,
        #                                 callback_data=str(admin)),
        #            InlineKeyboardButton('\U0000274C', callback_data='')
        #            )
        reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"The Admins:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user_id = update.callback_query.from_user.id
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == 'add_new_admin':
        await add_new_admin(update, context)
    elif choice == 'admin_list':
        await admin_list(update, context)
    elif choice == 'save_file':
        await save_file(update, context)
    elif choice == 'get_file':
        await get_file(update, context)


# async def handle_message(update: Update, context: CallbackContext):
#     if context.user_data.get('waiting_for_admin_id'):
#         try:
#             new_admin_id = int(update.message.text)
#             save_admin_to_db(new_admin_id)
#             await update.message.reply_text(f'Admin {new_admin_id} added successfully.')
#             context.user_data['waiting_for_admin_id'] = False  # Reset state
#         except ValueError:
#             await update.message.reply_text("Please use the command to add an admin.")
#     elif context.user_data.get('getting_file'):
#         file_id = update.message.text
#         await context.bot.send_document(chat_id=update.message.chat_id, document=file_id)
#         context.user_data['getting_file'] = False
#
#     context.user_data['getting_file'] = True


async def handle_url_message(update: Update, context: ContextTypes.DEFAULT_TYPE, f_id):

    result = get_file_from_db(f_id)
    if result:
        file_id = result.file_id
        await update.message.reply_text(download_time)
        await update.message.reply_text(download_time_fa)
        message = await context.bot.send_document(chat_id=update.effective_chat.id, document=file_id)
        asyncio.create_task(delete_message(message))
    else:
        await update.message.reply_text('invalid link')


async def delete_message(message):
    await asyncio.sleep(30)
    await message.delete()


async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Send The File: ")
    # Set a state to expect the next message as the new admin ID
    context.user_data['sending_file'] = True


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('sending_file'):
        document = update.message.document
        file_id = document.file_id
        context.user_data['sending_file'] = False
        # Prompt the user for the anime name
        await update.message.reply_text('please enter anime name:')
        context.user_data['file_id'] = file_id
        context.user_data['awaiting_anime_name'] = True
    else:
        await update.message.reply_text('not for upload files!')


async def handle_file_details(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get('awaiting_anime_name'):
        anime_name = update.message.text
        context.user_data['anime_name'] = anime_name

        # Prompt the user for the file number
        await update.message.reply_text('Please enter the file number:')
        context.user_data['awaiting_file_number'] = True
        context.user_data['awaiting_anime_name'] = False  # Reset state for file name
    elif context.user_data.get('awaiting_file_number'):
        file_number = update.message.text
        context.user_data['file_number'] = file_number

        # Prompt the user for the file version
        await update.message.reply_text('Please enter the file version:')
        context.user_data['awaiting_file_version'] = True
        context.user_data['awaiting_file_number'] = False  # Reset state for file number
    elif context.user_data.get('awaiting_file_version'):
        file_version = update.message.text
        file_id = context.user_data.get('file_id')
        anime_name = context.user_data.get('anime_name')
        file_number = context.user_data.get('file_number')

        # Save the file details (name, number, version, and file_id) to your database
        record_id = save_file_to_db(file_id, anime_name, file_number, file_version)
        file_link = 'https://t.me/nakama_v1_bot?start=' + str(record_id)

        await update.message.reply_text(
            f'File of {anime_name} saved successfully with number {file_number} and '
            f'version {file_version} and ID: {record_id}. Link: {file_link}'
        )
        episode_added = f'''\-\-\- 

🎬 \#{anime_name} Episode {file_number} is here\! 🎉

✨ Resolutions Available\:
{file_version} 🔥 
[Download Link]({file_link})
Enjoy watching\! 🍿✨

\-\-\-'''
        await context.bot.send_message(chat_id='@nakama_top', text=episode_added, parse_mode='MarkdownV2')
        # Reset state variables
        context.user_data['awaiting_file_version'] = False
    elif context.user_data.get('waiting_for_admin_id'):
        try:
            new_admin_id = int(update.message.text)
            save_admin_to_db(new_admin_id)
            await update.message.reply_text(f'Admin {new_admin_id} added successfully.')
            context.user_data['waiting_for_admin_id'] = False  # Reset state
        except ValueError:
            await update.message.reply_text("Please use the command to add an admin.")
    elif context.user_data.get('getting_file'):
        f_id = update.message.text
        await handle_url_message(update, context, f_id)
        context.user_data['getting_file'] = False

    else:
        await update.message.reply_text('Unexpected state!')


async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="File ID: ")
    context.user_data['getting_file'] = True


if __name__ == '__main__':
    init_db()
    print('Starting The Bot...')
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_file_details))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    application.run_polling()
