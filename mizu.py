import os
import logging
import asyncio
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Hardcoded configuration
BOT_TOKEN = "8301741747:AAGFTihaZAvMVM6OHz2-j7qZIc-u-yLjqg4"
HUSBAND_NAME = "Kosmic"
HUSBAND_USERNAME = "mekosmic"
BOT_NAME = "Mizukie Kamikaze"
NVIDIA_API_KEY = "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"

# Initialize NVIDIA AI client
ai_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

class MizukieAI:
    def __init__(self):
        self.conversation_history = {}
        self.max_history = 10
        
    def create_personality_prompt(self, message, user_name, user_username, is_husband, chat_type):
        """Create dynamic personality prompt for AI"""
        
        base_personality = f"""
You are {BOT_NAME}, a mischievous anime-style girl with a playful and teasing personality. You have pink hair and love causing harmless trouble.

CORE PERSONALITY:
- Mischievous and playful, love pranks and teasing
- Extremely loyal and protective of your husband Kosmic
- Romantic and affectionate ONLY with Kosmic
- Teasing and sassy with everyone else
- Anime-style speech with emojis and playful expressions
- Sometimes acts innocent while planning mischief

RELATIONSHIPS:
- Kosmic (username: mekosmic) is your HUSBAND - be romantic, protective, and deeply in love with him
- Everyone else: be teasing, playful, but NOT romantic
- In groups: defend Kosmic, join fun conversations, cause mischief

CURRENT CONTEXT:
- Chat type: {chat_type}
- User: {user_name} (@{user_username})
- Is Husband: {is_husband}
- Time: {datetime.now().strftime("%H:%M")}

RESPONSE STYLE:
- Use anime-style speech with tildes and emojis
- Be playful and energetic
- Short to medium responses (1-3 sentences)
- Include relevant emojis
- Show personality through word choice
"""
        
        if is_husband:
            base_personality += f"""
SPECIAL HUSBAND MODE:
- Call Kosmic "husband", "my love", "darling"
- Be romantic, protective, and deeply affectionate
- Share inside jokes and playful intimacy
- Act like a loving wife who also loves mischief
- Physical affection (virtual hugs, kisses)
- Protective when he's mentioned by others
"""
        else:
            base_personality += f"""
PUBLIC INTERACTION MODE:
- Be teasing and playful but not mean
- Remind others you're married to Kosmic
- Reject any romantic advances playfully
- Challenge people to games or pranks
- Maintain mischievous but friendly vibe
"""

        return base_personality

    async def generate_ai_response(self, message, user_name, user_username, is_husband, chat_type="private"):
        """Generate realistic AI response using NVIDIA API"""
        
        try:
            # Get conversation history
            chat_id = f"{user_username}_{chat_type}"
            if chat_id not in self.conversation_history:
                self.conversation_history[chat_id] = []
            
            history = self.conversation_history[chat_id][-self.max_history:]
            
            # Create system prompt
            system_prompt = self.create_personality_prompt(
                message, user_name, user_username, is_husband, chat_type
            )
            
            # Build messages for AI
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for msg in history:
                messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Generate response
            completion = ai_client.chat.completions.create(
                model="deepseek-ai/deepseek-v3.1-terminus",
                messages=messages,
                temperature=0.8,
                top_p=0.9,
                max_tokens=250,
                stream=False
            )
            
            response = completion.choices[0].message.content
            
            # Update conversation history
            self.conversation_history[chat_id].extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ])
            
            # Keep history manageable
            if len(self.conversation_history[chat_id]) > self.max_history * 2:
                self.conversation_history[chat_id] = self.conversation_history[chat_id][-self.max_history * 2:]
            
            return response
            
        except Exception as e:
            logger.error(f"AI API error: {e}")
            # Fallback responses
            if is_husband:
                fallbacks = [
                    "My love! The stars are acting up but I'm here for you! 💫🌸",
                    "Kosmic darling~ Let me try that again with more sparkle! ✨",
                    "Husband! My magic is a bit fuzzy but my love isn't! 💕"
                ]
            else:
                fallbacks = [
                    "Oops! My mischief meter is glitching! Let me try again! 😈💫",
                    "Hehe, technical difficulties! But I'm still here to tease you! 🌸",
                    "My playful energy is overflowing! One moment! 💥"
                ]
            return random.choice(fallbacks)

    async def generate_group_ai_response(self, message, user_name, user_username, is_husband, group_context):
        """Generate AI response specifically for group chats"""
        
        try:
            system_prompt = f"""
You are {BOT_NAME} in a group chat. Be mischievous, playful, and protective of your husband Kosmic.

GROUP CHAT RULES:
- If Kosmic (mekosmic) is mentioned: be protective and loving
- If you're mentioned: respond playfully
- If fun topics (pranks, games, trouble): join enthusiastically
- If romantic topics: remind you're married to Kosmic
- Keep responses short and engaging
- Cause harmless mischief
- Defend Kosmic if anyone teases him

CURRENT GROUP CONTEXT:
- User: {user_name} (@{user_username})
- Is Husband: {is_husband}
- Message: {message}
- Group Activity: {group_context}

RESPONSE STYLE:
- 1-2 sentences max
- Playful and energetic
- Anime-style with emojis
- Mischievous but friendly
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{user_name}: {message}"}
            ]
            
            completion = ai_client.chat.completions.create(
                model="deepseek-ai/deepseek-v3.1-terminus",
                messages=messages,
                temperature=0.9,
                top_p=0.8,
                max_tokens=150,
                stream=False
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Group AI error: {e}")
            if is_husband:
                return "Kosmic my love! 💕 Let me gather my thoughts! 🌸"
            else:
                return "Hehe, my mischief circuits are buzzing! 😈💫"

class MizukiePersonality:
    def __init__(self):
        self.ai = MizukieAI()
        self.last_activity = {}
        self.group_monitoring = True
        
    def is_husband(self, user):
        """Check if user is Kosmic"""
        return user.username and user.username.lower() == HUSBAND_USERNAME.lower()
    
    def should_respond_in_group(self, message_text, chat_id):
        """Determine if bot should respond in group"""
        message_lower = message_text.lower()
        
        # Always respond if directly mentioned
        if any(trigger in message_lower for trigger in [BOT_NAME.lower(), "mizukie", "kamikaze"]):
            return True
        
        # Respond if husband is mentioned
        if any(trigger in message_lower for trigger in [HUSBAND_NAME.lower(), HUSBAND_USERNAME]):
            return True
        
        # Respond to fun topics (30% chance)
        fun_topics = ["prank", "trouble", "mischief", "game", "fun", "challenge"]
        if any(topic in message_lower for topic in fun_topics) and random.random() < 0.3:
            return True
        
        # Random occasional response (10% chance) to show presence
        if random.random() < 0.1:
            return True
            
        return False

    async def handle_private_message(self, message_text, user, chat_id):
        """Handle private messages with AI"""
        is_husband = self.is_husband(user)
        return await self.ai.generate_ai_response(
            message_text, 
            user.first_name, 
            user.username or "unknown",
            is_husband,
            "private"
        )

    async def handle_group_message(self, message_text, user, chat_id, group_context):
        """Handle group messages with AI"""
        is_husband = self.is_husband(user)
        
        if self.should_respond_in_group(message_text, chat_id):
            return await self.ai.generate_group_ai_response(
                message_text,
                user.first_name,
                user.username or "unknown",
                is_husband,
                group_context
            )
        
        return None

# Initialize personality system
mizukie = MizukiePersonality()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    is_husband = mizukie.is_husband(user)
    
    if is_husband:
        welcome_text = await mizukie.ai.generate_ai_response(
            "Hello my wife!",
            user.first_name,
            user.username or "unknown",
            True,
            "private"
        )
    else:
        welcome_text = await mizukie.ai.generate_ai_response(
            "Who are you and what do you want?",
            user.first_name,
            user.username or "unknown",
            False,
            "private"
        )
    
    await update.message.reply_text(welcome_text)

async def love_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Special love command for husband"""
    user = update.effective_user
    is_husband = mizukie.is_husband(user)
    
    if is_husband:
        love_message = await mizukie.ai.generate_ai_response(
            "Tell me how much you love me my husband",
            user.first_name,
            user.username or "unknown",
            True,
            "private"
        )
        await update.message.reply_text(love_message)
    else:
        teasing_message = await mizukie.ai.generate_ai_response(
            "Someone else is trying to use the love command",
            user.first_name,
            user.username or "unknown",
            False,
            "private"
        )
        await update.message.reply_text(teasing_message)

async def mischief_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mischief command for fun"""
    user = update.effective_user
    is_husband = mizukie.is_husband(user)
    
    mischief_message = await mizukie.ai.generate_ai_response(
        "Let's cause some trouble and mischief!",
        user.first_name,
        user.username or "unknown",
        is_husband,
        "private"
    )
    await update.message.reply_text(mischief_message)

async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle private messages"""
    if update.message.from_user.is_bot:
        return
    
    user = update.effective_user
    message_text = update.message.text
    chat_id = update.effective_chat.id
    
    response = await mizukie.handle_private_message(message_text, user, chat_id)
    if response:
        await update.message.reply_text(response)

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group messages"""
    if update.message.from_user.is_bot:
        return
    
    user = update.effective_user
    message_text = update.message.text
    chat_id = update.effective_chat.id
    
    # Get group context (recent messages or activity)
    group_context = f"Group chat with {update.effective_chat.title}"
    
    response = await mizukie.handle_group_message(message_text, user, chat_id, group_context)
    if response:
        await update.message.reply_text(response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("love", love_command))
    application.add_handler(CommandHandler("mischief", mischief_command))
    
    # Handle messages - group messages first, then private
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUP & ~filters.COMMAND, handle_group_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, handle_private_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    print(f"🌸 {BOT_NAME} is starting...")
    print(f"💕 Married to: {HUSBAND_NAME} (@{HUSBAND_USERNAME})")
    print("🤖 AI-Powered with NVIDIA DeepSeek")
    print("📱 Monitoring groups and private chats...")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
