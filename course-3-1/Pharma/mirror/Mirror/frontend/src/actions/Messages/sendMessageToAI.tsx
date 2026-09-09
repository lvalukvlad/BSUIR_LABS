export default async function sendMessageToAI(id: number, text: string, chat: number){
  // return {success: true, text: 'Первые шаги'}
  try {
    // Используем orchestration-service вместо прямого обращения к KP сервису
    // В браузере всегда используем localhost, так как Docker hostname не работает в браузере
    const apiUrl = 'http://localhost:8084'
    const response = await fetch(`${apiUrl}/api/chat/new/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        message: text,
        chatId: chat,
        userId: id
      }),
    })
    console.log(response)
    if (!response.ok) {
      const errorText = await response.text()
      console.error('Ошибка при отправке сообщения:', errorText)
      throw new Error('Ошибка анализа: ' + errorText)
    }
    const data = await response.json()
    // История сохраняется автоматически в orchestration-service
    return { chatId: chat, response: data.response }
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Произошла ошибка при анализе')
  }

}