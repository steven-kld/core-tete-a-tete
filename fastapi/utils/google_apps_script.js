function doPost(e) {
  const required = ["sheet_id", "id", "message", "title", "description", "app_url", "group_name", "username", "chat_id", "token"]
  const missing = required.filter(k => !e.parameter[k])
  if (missing.length > 0) {
    return ContentService.createTextOutput(
      JSON.stringify({ success: false, error: "Missing required parameters"})
    ).setMimeType(ContentService.MimeType.JSON)
  }

  try {
    const data = e.parameter
    const row = [
      new Date().toDateString(),
      data.id,
      data.message,
      data.title,
      data.description,
      data.username,
      data.app_url,
      data.group_name,
    ]

    const sheet = SpreadsheetApp.openById(data.sheet_id).getSheetByName('Main')
    sheet.insertRows(2)
    sheet.getRange(2, 1, 1, row.length).setValues([row])

    sendTelegramMessage(`GROUP: ${data.group_name}\nID ${data.id}:\n${data.description}`, data.chat_id, data.token)

    return ContentService.createTextOutput(JSON.stringify({
      success: true,
      message: 'Inserted successfully'
    })).setMimeType(ContentService.MimeType.JSON)

  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ success: false, error: err.message })
    ).setMimeType(ContentService.MimeType.JSON)
  }
}
  
function sendTelegramMessage(message, chatId, token) {
  const url = `https://api.telegram.org/bot${token}/sendMessage`
  const payload = {
    chat_id: chatId,
    text: message,
  }
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
  }
  const response = UrlFetchApp.fetch(url, options)
  Logger.log(response.getContentText())
}
  
// Run once to detect chat_id
function getBotUpdates() {
  const token = '' // Manually add your token here
  const url = `https://api.telegram.org/bot${token}/getUpdates`
  const options = {
    method: 'get',
    contentType: 'application/json'
  }
  const response = UrlFetchApp.fetch(url, options)
  Logger.log(response.getContentText())
}