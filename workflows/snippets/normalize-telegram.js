const message = $json.message || {};

return [
  {
    json: {
      messageType: message.voice ? "voice" : "text",
      chatId: message.chat?.id,
      telegramUserId: message.from?.id ? String(message.from.id) : null,
      telegramUsername: message.from?.username || null,
      text: message.text || "",
      voiceFileId: message.voice?.file_id || null,
    },
  },
];
