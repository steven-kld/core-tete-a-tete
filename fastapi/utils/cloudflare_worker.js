export default {
  async fetch(request, env, ctx) {
    if (request.method === 'POST') {
      const b = await request.text();
      const parsed = JSON.parse(b);

      if (!parsed.message) {
        if (parsed.chat_id) {
          const msg = `${parsed.title}\n\n${parsed.message_raw}\n\n#########\nTG: ${parsed.username}\nURL: ${parsed.app_url}`
          const sendResult = await sendTelegramMessage(env.BOT_TOKEN, parsed.chat_id, msg);
          console.log('Telegram send result:', sendResult);
        }
        return new Response('OK', { status: 200 });
      }

      if (parsed.message.text === '/start') {
        const chatId = parsed.message.chat.id;
    
        // Await server response
        const serverRes = await fetch('https://watch.tete-a-tete.ge/api/bot/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            bot: env.BOT_NAME,
            tg: parsed
          })
        });
        const { status } = await serverRes.json();
    
        let reply;
        if (status === true) {
          reply = "Привет, теперь все работает!\nУведомления будут приходить прямо в этот чат";
        } else {
          reply = "Привет! Похоже, вы еще не зарегистрировались, обратитесь к администратору";
        }
    
        // Now send the correct Telegram message
        const sendResult = await sendTelegramMessage(env.BOT_TOKEN, chatId, reply);
        console.log('Telegram send result:', sendResult);
    
        return new Response('OK', { status: 200 });
      }

      return new Response('OK', { status: 200 });
    }
    return new Response('Not allowed', { status: 405 });
  }
}

async function sendTelegramMessage(token, chatId, text) {
  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  const body = JSON.stringify({
    chat_id: chatId,
    text: text
  });
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body
  });

  // Only parse JSON once
  const result = await resp.json();
  return result;
}
