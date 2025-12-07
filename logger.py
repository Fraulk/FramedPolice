import asyncio
from datetime import datetime
from collections import deque
from dotenv import load_dotenv
import os

load_dotenv()

# Import LogChannel from vars
from vars import LogChannel

# Config
LOG_CHANNEL_ID = LogChannel
BUFFER_INTERVAL = 10  # send bundled logs every 10 sec (was 60)
MAX_DISCORD_MESSAGE = 2000  # Discord message char limit
MAX_LOGS_PER_MESSAGE = 200  # Max lines per message (was 50)

class LogBuffer:
    def __init__(self, bot):
        self.bot = bot
        self.buffer = deque(maxlen=1000)  # Keep last 1000 logs in memory
        self.lock = asyncio.Lock()
        self.running = False
    
    async def add_log(self, message: str):
        """Add log to buffer"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        async with self.lock:
            self.buffer.append(log_entry)
    
    async def flush_logs(self):
        """Send all buffered logs to Discord"""
        if not LOG_CHANNEL_ID or LOG_CHANNEL_ID == 0:
            print(f"[LOGGER] No channel ID set: {LOG_CHANNEL_ID}")
            return
        
        async with self.lock:
            if not self.buffer:
                return
            
            logs = list(self.buffer)
            self.buffer.clear()
        
        print(f"[LOGGER] Fetching channel {LOG_CHANNEL_ID}...")
        channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if not channel:
            print(f"[LOGGER] Can't find channel {LOG_CHANNEL_ID}. Available: {[c.id for c in self.bot.get_all_channels()]}")
            return
        
        print(f"[LOGGER] Found channel: {channel.name}")
        
        # Split into discord compatible messages
        messages = self._split_messages(logs)
        
        print(f"[LOGGER] Sending {len(messages)} message(s)...")
        for msg in messages:
            await self._send_to_discord(channel, msg)
    
    def _split_messages(self, logs):
        """Split logs into Discord-compatible messages"""
        messages = []
        current_msg = ""
        current_lines = 0
        
        for log in logs:
            if (len(current_msg) + len(log) + 1 > MAX_DISCORD_MESSAGE or 
                current_lines >= MAX_LOGS_PER_MESSAGE):
                if current_msg:
                    messages.append(current_msg)
                current_msg = log + "\n"
                current_lines = 1
            else:
                current_msg += log + "\n"
                current_lines += 1
        
        if current_msg:
            messages.append(current_msg)
        
        return messages
    
    async def _send_to_discord(self, channel, content: str):
        """Send message to Discord channel"""
        try:
            await channel.send(f"```\n{content}\n```")
        except Exception as e:
            print(f"[LOGGER] Failed to send to Discord: {e}")
    
    async def start_flusher(self):
        """Start background task that flushes logs periodically"""
        self.running = True
        try:
            while self.running:
                await asyncio.sleep(BUFFER_INTERVAL)
                await self.flush_logs()
        except asyncio.CancelledError:
            # Flush remaining logs on shutdown
            await self.flush_logs()
            self.running = False
    
    def stop_flusher(self):
        """Stop background flusher"""
        self.running = False

# Global instance - will be initialized in framed_police.py
class _LogBufferContainer:
    instance = None




async def log_to_hof(message: str):
    """Log HOF-related stuff"""
    print(f"[HOF] {message}")
    if _LogBufferContainer.instance:
        try:
            await _LogBufferContainer.instance.add_log(f"[HOF] {message}")
        except Exception as e:
            print(f"[LOGGER] Failed to add HOF log: {e}")

async def log_error(message: str):
    """Log errors"""
    print(f"[ERROR] {message}")
    if _LogBufferContainer.instance:
        try:
            await _LogBufferContainer.instance.add_log(f"[ERROR] {message}")
        except Exception as e:
            print(f"[LOGGER] Failed to add error log: {e}")

async def log_info(message: str):
    """Log info"""
    print(f"[INFO] {message}")
    if _LogBufferContainer.instance:
        try:
            await _LogBufferContainer.instance.add_log(f"[INFO] {message}")
        except Exception as e:
            print(f"[LOGGER] Failed to add info log: {e}")

def set_log_buffer(buffer):
    """Set the global log buffer instance"""
    _LogBufferContainer.instance = buffer

