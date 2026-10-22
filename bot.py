import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
)

# ------------------------------------------------------------------
# НАСТРОЙКИ И ТОКЕНЫ
# ------------------------------------------------------------------
TOKEN = "8870585910:AAHM-uICSqAzSlv1K5TMF_3nqNCXh9PC1C0"
SUPER_ADMIN_ID = 7942212896  # Андрей Романов (Супер Админ)
WEBSITE_URL = "https://your-website-domain.com"  # Ссылка на ваш сайт

bot = Bot(token=TOKEN)
router = Router()

# Активные диалоги поддержка <-> пользователь: {user_id: admin_id}
active_chats = {}

# База данных администраторов и санкций: {admin_id: {"role": ..., "warns": 0, "reprimands": 0}}
admins_db = {
    SUPER_ADMIN_ID: {
        "name": "Андрій Романов",
        "role": "Super Admin",
        "warns": 0,
        "reprimands": 0,
    }
}

# Множество зарегистрированных пользователей для рассылки
registered_users = set()


class SupportStates(StatesGroup):
  waiting_for_question = State()
  chat_with_admin = State()
  waiting_for_admin_id = State()
  waiting_for_broadcast_msg = State()


# ------------------------------------------------------------------
# ГЛАВНОЕ МЕНЮ И СТАРТ
# ------------------------------------------------------------------
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
  await state.clear()
  registered_users.add(message.from_user.id)

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="🎧 Задати питання / Підтримка", callback_data="support"
              )
          ],
          [
              InlineKeyboardButton(
                  text="🌊 Проєкти та реабілітація", callback_data="projects"
              ),
              InlineKeyboardButton(
                  text="🤝 Спільноти", callback_data="communities"
              ),
          ],
          [
              InlineKeyboardButton(
                  text="❓ Часті питання (FAQ)", callback_data="faq"
              )
          ],
          [
              InlineKeyboardButton(
                  text="🌐 Перейти на сайт Океан Дружніх", url=WEBSITE_URL
              )
          ],
      ]
  )

  wel_text = (
      f"Вітаю, {html.quote(message.from_user.first_name)}! 🇺🇦\n\n"
      "Ласкаво просимо до офіційного бота платформи **«Океан Дружніх»**.\n\n"
      "Я допоможу вам знайти потрібну інформацію, дізнатися про програми реабілітації "
      "або анонімно з'єднаю вас із нашим **Агентом підтримки**."
  )
  await message.answer(wel_text, reply_markup=keyboard, parse_mode="Markdown")


# ------------------------------------------------------------------
# ИНФОРМАЦИОННЫЕ РАЗДЕЛЫ
# ------------------------------------------------------------------
@router.callback_query(F.data == "projects")
async def cb_projects(callback: CallbackQuery):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="🎧 Зв'язатися з Агентом", callback_data="call_admin"
              )
          ],
          [
              InlineKeyboardButton(
                  text="« Головне меню", callback_data="back_to_menu"
              )
          ],
      ]
  )
  text = (
      "🌊 **Ключові проєкти платформи «Океан Дружніх»:**\n\n"
      "1. **Морські леви** — програма водного спорту та фізичної реабілітації захисников.\n"
      "2. **Upgradeus Mechanicus** — інженерний хаб та розробка технічних засобів.\n"
      "3. **Оберіг** — психологічна підтримка та допомога родинам.\n\n"
      "Бажаєте дізнатися більше або долучитися?"
  )
  await callback.message.edit_text(
      text, reply_markup=keyboard, parse_mode="Markdown"
  )
  await callback.answer()


@router.callback_query(F.data == "communities")
async def cb_communities(callback: CallbackQuery):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="🌐 Відкрити каталог на сайті", url=WEBSITE_URL
              )
          ],
          [
              InlineKeyboardButton(
                  text="« Головне меню", callback_data="back_to_menu"
              )
          ],
      ]
  )
  text = (
      "🤝 **Спільноти за інтересами:**\n\n"
      "Об'єднуємо побратимів та однодумців по всій Україні:\n"
      "• Море та водні види спорту\n"
      "• Інженерія та технології\n"
      "• Волонтерські осередки\n"
      "• Соціальна адаптація\n\n"
      "Повний перелік спільнот доступний у нашому каталозі на сайті."
  )
  await callback.message.edit_text(
      text, reply_markup=keyboard, parse_mode="Markdown"
  )
  await callback.answer()


@router.callback_query(F.data == "faq")
async def cb_faq(callback: CallbackQuery):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="🎧 Покликати Агента підтримки",
                  callback_data="call_admin",
              )
          ],
          [
              InlineKeyboardButton(
                  text="« Головне меню", callback_data="back_to_menu"
              )
          ],
      ]
  )
  text = (
      "❓ **Часті питання:**\n\n"
      "**1. Чи це повністю безкоштовно?**\n"
      "Так, усі програми та консультації на платформі надаються безкоштовно.\n\n"
      "**2. Чи зберігаються мої особисті дані?**\n"
      "Ні, спілкування з Агентом підтримки відбувається повністю анонімно.\n\n"
      "**3. Як отримати консультацію фахівця?**\n"
      "Натисніть кнопку нижче, щоб розпочати діалог."
  )
  await callback.message.edit_text(
      text, reply_markup=keyboard, parse_mode="Markdown"
  )
  await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def cb_back_to_menu(callback: CallbackQuery, state: FSMContext):
  await cmd_start(callback.message, state)
  await callback.answer()


# ------------------------------------------------------------------
# ЧАТ ПОДДЕРЖКИ И АНОНИМНЫЙ СЕАНС С АГЕНТОМ
# ------------------------------------------------------------------
@router.callback_query(F.data == "support")
async def cb_support(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="🎧 Покликати Агента підтримки",
                  callback_data="call_admin",
              )
          ],
          [
              InlineKeyboardButton(
                  text="« Головне меню", callback_data="back_to_menu"
              )
          ],
      ]
  )
  await callback.message.edit_text(
      "💬 Напишіть ваше запитання нижче. Наш автоматичний помічник надасть первинну інформацію, "
      "або ви можете одразу з'єднатися з живим Агентом підтримки.",
      reply_markup=keyboard,
  )
  await state.set_state(SupportStates.waiting_for_question)
  await callback.answer()


@router.message(SupportStates.waiting_for_question)
async def ai_assistant_handler(message: Message, state: FSMContext):
  text = message.text.lower()

  if "реабілітаці" in text or "лікуванн" in text:
    reply = (
        "🏥 **Реабілітація:**\nПрограма «Морські леви» надає безкоштовну підтримку. "
        "Бажаєте з'єднатися з Агентом підтримки для оформлення заявки?"
    )
  else:
    reply = (
        "🤖 Запит зафіксовано. Натисніть кнопку нижче, щоб перенаправити "
        "діалог до живого Агента підтримки."
    )

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="🎧 З'єднати з Агентом підтримки",
                  callback_data="call_admin",
              )
          ]
      ]
  )
  await message.answer(reply, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "call_admin")
async def call_admin_handler(callback: CallbackQuery, state: FSMContext):
  user_id = callback.from_user.id

  if not admins_db:
    await callback.message.answer("⏳ Наразі немає вільних Агентів підтримки.")
    await callback.answer()
    return

  admin_id = list(admins_db.keys())[0]

  active_chats[user_id] = admin_id
  active_chats[admin_id] = user_id

  await state.set_state(SupportStates.chat_with_admin)

  await callback.message.answer(
      "🔒 **Анонімний сеанс з Агентом підтримки активовано!**\n\n"
      "Ваші особисті дані та Username приховані. Всі повідомлення передаються оператору.\n"
      "Для завершення діалогу введіть /stop"
  )

  admin_keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="❌ Закрити тікет", callback_data=f"close_chat_{user_id}"
              )
          ]
      ]
  )
  await bot.send_message(
      admin_id,
      f"🚨 **Новий анонімний запит у підтримку!**\n"
      f"ID тікета: `ID-{user_id}`\n\n"
      f"Напишіть відповідь нижче, і вона буде надіслана користувачу.",
      reply_markup=admin_keyboard,
      parse_mode="Markdown",
  )
  await callback.answer()


@router.message(SupportStates.chat_with_admin)
async def relay_chat_messages(message: Message):
  sender_id = message.from_user.id
  receiver_id = active_chats.get(sender_id)

  if not receiver_id:
    await message.answer(
        "⚠️ Активний діалог завершено. Натисніть /start для виходу в меню."
    )
    return

  if message.text and message.text.lower() == "/stop":
    active_chats.pop(sender_id, None)
    active_chats.pop(receiver_id, None)
    await message.answer("🔒 Діалог з підтримкою завершено.")
    await bot.send_message(receiver_id, "🔒 Агент підтримки завершив діалог.")
    return

  # ПЕРЕСЫЛКА СООБЩЕНИЙ (ИЗМЕНЕНО НА "Агент підтримки")
  if sender_id in admins_db:
    await bot.send_message(
        receiver_id, f"🎧 **Агент підтримки:**\n{message.text}"
    )
  else:
    await bot.send_message(
        receiver_id, f"📩 **Звернення (Тікет #{sender_id}):**\n{message.text}"
    )


@router.callback_query(F.data.startswith("close_chat_"))
async def close_chat_callback(callback: CallbackQuery):
  user_id = int(callback.data.split("_")[2])
  admin_id = callback.from_user.id

  active_chats.pop(user_id, None)
  active_chats.pop(admin_id, None)

  await callback.message.edit_text("✅ Тікет успішно закрито.")
  await bot.send_message(
      user_id, "🔒 Анонімний сеанс завершено Агентом підтримки."
  )
  await callback.answer()


# ------------------------------------------------------------------
# РАСШИРЕННАЯ АДМИН-ПАНЕЛЬ С САНКЦИЯМИ И УПРАВЛЕНИЕМ КОМАНДОЙ
# ------------------------------------------------------------------
@router.message(Command("admin"))
async def cmd_admin_panel(message: Message):
  if message.from_user.id not in admins_db:
    await message.answer("⛔ **Доступ заборонено!** Ви не є адміністратором.")
    return

  admin_data = admins_db[message.from_user.id]

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="👥 Список адміністраторів & Санкції",
                  callback_data="admin_team",
              )
          ],
          [
              InlineKeyboardButton(
                  text="➕ Додати адміна", callback_data="add_admin_start"
              ),
              InlineKeyboardButton(
                  text="➖ Видалити адміна", callback_data="del_admin_start"
              ),
          ],
          [
              InlineKeyboardButton(
                  text="📢 Масова розсилка", callback_data="broadcast_start"
              )
          ],
          [
              InlineKeyboardButton(
                  text="📊 Статистика бота", callback_data="admin_stats"
              )
          ],
      ]
  )

  text = (
      f"🛡 **Панель Адміністратора**\n\n"
      f"• **Користувач:** {admin_data.get('name', 'Admin')}\n"
      f"• **Посада:** {admin_data['role']}\n"
      f"• **Попереджень:** {admin_data['warns']} | **Доган:** {admin_data['reprimands']}\n\n"
      f"Оберіть потрібну дію в меню ниже:"
  )
  await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "admin_team")
async def cb_admin_team(callback: CallbackQuery):
  if callback.from_user.id not in admins_db:
    return

  text = "👥 **Команда адміністрації та санкції:**\n\n"
  buttons = []

  for aid, data in admins_db.items():
    text += (
        f"• **{data.get('name', 'Admin')}** (ID: `{aid}`)\n"
        f"  Роль: {data['role']} | ⚠️ Попереджень: {data['warns']} | 🛑 Доган: {data['reprimands']}\n\n"
    )
    if aid != SUPER_ADMIN_ID:
      buttons.append([
          InlineKeyboardButton(
              text=f"⚠️ +Попер. ({data.get('name', aid)})",
              callback_data=f"warn_{aid}",
          ),
          InlineKeyboardButton(
              text=f"🛑 +Догана ({data.get('name', aid)})",
              callback_data=f"rep_{aid}",
          ),
      ])
      buttons.append([
          InlineKeyboardButton(
              text=f"🧹 Очистити санкції ({aid})",
              callback_data=f"clear_sanctions_{aid}",
          )
      ])

  buttons.append(
      [InlineKeyboardButton(text="« Назад в Адмінку", callback_data="back_admin")]
  )
  keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

  await callback.message.edit_text(
      text, reply_markup=keyboard, parse_mode="Markdown"
  )
  await callback.answer()


@router.callback_query(F.data.startswith("warn_"))
async def cb_add_warn(callback: CallbackQuery):
  target_id = int(callback.data.split("_")[1])
  if target_id in admins_db:
    admins_db[target_id]["warns"] += 1
    await callback.answer(
        f"⚠️ Попередження додано! Всього: {admins_db[target_id]['warns']}"
    )
    await cb_admin_team(callback)


@router.callback_query(F.data.startswith("rep_"))
async def cb_add_rep(callback: CallbackQuery):
  target_id = int(callback.data.split("_")[1])
  if target_id in admins_db:
    admins_db[target_id]["reprimands"] += 1
    await callback.answer(
        f"🛑 Догану додано! Всього: {admins_db[target_id]['reprimands']}"
    )
    await cb_admin_team(callback)


@router.callback_query(F.data.startswith("clear_sanctions_"))
async def cb_clear_sanctions(callback: CallbackQuery):
  target_id = int(callback.data.split("_")[2])
  if target_id in admins_db:
    admins_db[target_id]["warns"] = 0
    admins_db[target_id]["reprimands"] = 0
    await callback.answer("🧹 Усі санкції та догани знято!")
    await cb_admin_team(callback)


@router.callback_query(F.data == "add_admin_start")
async def cb_add_admin_start(callback: CallbackQuery, state: FSMContext):
  if callback.from_user.id != SUPER_ADMIN_ID:
    await callback.answer(
        "⛔ Тільки Super Admin може додавати нових адміністраторів!",
        show_alert=True,
    )
    return

  await callback.message.answer(
      "Введіть Telegram ID нового адміністратора (наприклад: `123456789`):"
  )
  await state.set_state(SupportStates.waiting_for_admin_id)
  await callback.answer()


@router.message(SupportStates.waiting_for_admin_id)
async def process_add_admin_id(message: Message, state: FSMContext):
  try:
    new_id = int(message.text.trim())
    admins_db[new_id] = {
        "name": f"Адмін #{new_id}",
        "role": "Агент підтримки",
        "warns": 0,
        "reprimands": 0,
    }
    await message.answer(
        f"✅ Користувача `{new_id}` успішно призначено Агентом підтримки!",
        parse_mode="Markdown",
    )
  except ValueError:
    await message.answer("❌ Помилка! Введіть числовий Telegram ID.")
  await state.clear()


@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
  text = (
      f"📊 **Статистика системи «Океан Дружніх»:**\n\n"
      f"• Всього користувачів у боті: **{len(registered_users)}**\n"
      f"• Активних Агентів підтримки: **{len(admins_db)}**\n"
      f"• Відкритих анонімних чатів: **{len(active_chats) // 2}**"
  )
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="« Назад в Адмінку", callback_data="back_admin"
              )
          ]
      ]
  )
  await callback.message.edit_text(
      text, reply_markup=keyboard, parse_mode="Markdown"
  )
  await callback.answer()


@router.callback_query(F.data == "back_admin")
async def cb_back_admin(callback: CallbackQuery):
  admin_data = admins_db[callback.from_user.id]
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="👥 Список адміністраторів & Санкції",
                  callback_data="admin_team",
              )
          ],
          [
              InlineKeyboardButton(
                  text="➕ Додати адміна", callback_data="add_admin_start"
              )
          ],
          [
              InlineKeyboardButton(
                  text="📊 Статистика бота", callback_data="admin_stats"
              )
          ],
      ]
  )
  text = (
      f"🛡 **Панель Адміністратора**\n\n"
      f"• **Користувач:** {admin_data.get('name', 'Admin')}\n"
      f"• **Посада:** {admin_data['role']}\n"
  )
  await callback.message.edit_text(
      text, reply_markup=keyboard, parse_mode="Markdown"
  )
  await callback.answer()


# ------------------------------------------------------------------
# ЗАПУСК БОТА
# ------------------------------------------------------------------
async def main():
  logging.basicConfig(level=logging.INFO)
  dp = Dispatcher()
  dp.include_router(router)
  await bot.delete_webhook(drop_pending_updates=True)
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())