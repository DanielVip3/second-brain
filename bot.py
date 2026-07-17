import os
import uuid
from dotenv import load_dotenv
from telegram import MessageEntity as PTBMessageEntity, Update, User as PTBUser
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegramify_markdown.stream import DraftStream
from agent import ask_agent

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_IDS = [int(os.getenv("TELEGRAM_ADMIN_USER_ID", 0))]

user_threads = {}

def get_thread_id(user_id: int) -> str:
  if user_id not in user_threads:
    user_threads[user_id] = str(uuid.uuid4())
  return user_threads[user_id]

def reset_thread_id(user_id: int):
  user_threads[user_id] = str(uuid.uuid4())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if update.effective_user.id not in ALLOWED_USER_IDS:
    print(f"Unauthorized access by: {update.effective_user.id}")
    return
  
  await update.message.reply_text("👋🏻 Hi, it's 2Brain. Ask me anything.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  chat_id = update.effective_chat.id
    
  if user_id not in ALLOWED_USER_IDS:
    print(f"Unauthorized access by: {user_id}")
    return

  user_message = update.message.text
  thread_id = get_thread_id(user_id)

  draft_id = update.message.message_id
  
  await context.bot.send_chat_action(chat_id=chat_id, action="typing")

  await update.message.reply_text_draft(draft_id=draft_id, text="⏳ Thinking")

  def to_ptb_entities(entities):
    result = []
    for e in entities:
      user = PTBUser(**e.user) if getattr(e, "user", None) else None
      result.append(PTBMessageEntity(
        type=e.type,
        offset=e.offset,
        length=e.length,
        url=getattr(e, "url", None),
        language=getattr(e, "language", None),
        custom_emoji_id=getattr(e, "custom_emoji_id", None),
        user=user,
      ))
    return result
  
  async def send_draft(payload):
    await update.message.reply_text_draft(
      draft_id=draft_id,
      text=payload.text,
      entities=to_ptb_entities(payload.entities)
    )

  async def send_final(payload):
    await update.message.reply_text(
      text=payload.text,
      entities=to_ptb_entities(payload.entities)
    )
  
  def new_stream(send_draft, send_final):
    return DraftStream(
      send_draft=send_draft,
      send_final=send_final,
      mode="entity",
      interval=0.5,
      thinking_delay=0.5,
      keepalive_timeout=60.0
    )

  try:
    async with new_stream(send_draft, send_final) as stream:
      async for item in ask_agent(user_message, thread_id):
        if item["type"] == "token":
          stream.feed(item["content"])
        
        elif item["type"] == "tool_status":
          print(item["content"])
        
        elif item["type"] == "memory_wiped":
          reset_thread_id(user_id)
          print(f"[System: The agent wiped memory for user {user_id}.]")
        
        elif item["type"] == "error":
          raise Exception(item["content"])

      await stream.finish()
  except Exception as e:
    await update.message.reply_text(f"❌ An error occurred: {str(e)}")
    print(f"Error: {e}")

if __name__ == "__main__":
  if not TELEGRAM_BOT_TOKEN:
    print("You did not set the TELEGRAM_BOT_TOKEN environment variable.")
    exit(1)
  
  if not ALLOWED_USER_IDS:
    print("You have not specified any allowed users.")
    exit(1)

  app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

  app.add_handler(CommandHandler("start", start))
  app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

  print("Telegram bot running.")
  app.run_polling()