using Microsoft.AspNetCore.Mvc;
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Threading;

namespace SalesAssistantAPI.Controllers;

[Route("api/sales")]
[ApiController]
public class SalesAssistantController : ControllerBase
{
    private readonly HttpClient _httpClient;
    private readonly string _apiKey;
    private readonly string _assistantId;

    public SalesAssistantController()
    {
        _httpClient = new HttpClient();
        _apiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY") ?? "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";
        _assistantId = "asst_Sf96owAWcAFqaAkdVKt377Fi";  
    }

    [HttpGet("ask")]
    public async Task<IActionResult> AskQuestion([FromQuery] string question)
    {
        if (string.IsNullOrEmpty(question))
        {
            return BadRequest(new { error = "Question cannot be empty." });
        }

        try
        {
            // 1. create a new chat -  Thread
            var threadRequest = new { };
            var threadRequestContent = new StringContent(JsonSerializer.Serialize(threadRequest), Encoding.UTF8, "application/json");

            _httpClient.DefaultRequestHeaders.Clear();
            _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiKey}");
            _httpClient.DefaultRequestHeaders.Add("OpenAI-Beta", "assistants=v2");

            var threadResponse = await _httpClient.PostAsync("https://api.openai.com/v1/threads", threadRequestContent);
            threadResponse.EnsureSuccessStatusCode();
            var threadResponseBody = await threadResponse.Content.ReadAsStringAsync();
            var threadId = JsonDocument.Parse(threadResponseBody).RootElement.GetProperty("id").GetString();

            // 2. send user's question
            var messageRequest = new
            {
                role = "user",
                content = question
            };
            var messageRequestContent = new StringContent(JsonSerializer.Serialize(messageRequest), Encoding.UTF8, "application/json");

            var messageResponse = await _httpClient.PostAsync($"https://api.openai.com/v1/threads/{threadId}/messages", messageRequestContent);
            messageResponse.EnsureSuccessStatusCode();

            // 3. Assistant
            var runRequest = new { assistant_id = _assistantId };
            var runRequestContent = new StringContent(JsonSerializer.Serialize(runRequest), Encoding.UTF8, "application/json");

            var runResponse = await _httpClient.PostAsync($"https://api.openai.com/v1/threads/{threadId}/runs", runRequestContent);
            runResponse.EnsureSuccessStatusCode();
            var runResponseBody = await runResponse.Content.ReadAsStringAsync();
            var runId = JsonDocument.Parse(runResponseBody).RootElement.GetProperty("id").GetString();

            // 4️. waiting for completed 
            string runStatus;
            do
            {
                await Task.Delay(2000); // every 2s
                var runStatusResponse = await _httpClient.GetAsync($"https://api.openai.com/v1/threads/{threadId}/runs/{runId}");
                runStatusResponse.EnsureSuccessStatusCode();
                var runStatusBody = await runStatusResponse.Content.ReadAsStringAsync();
                runStatus = JsonDocument.Parse(runStatusBody).RootElement.GetProperty("status").GetString();
            } while (runStatus != "completed");

            // 5️. get respond from assistant API
            var messagesResponse = await _httpClient.GetAsync($"https://api.openai.com/v1/threads/{threadId}/messages");
            messagesResponse.EnsureSuccessStatusCode();
            var messagesBody = await messagesResponse.Content.ReadAsStringAsync();
            var messagesJson = JsonDocument.Parse(messagesBody).RootElement.GetProperty("data");

            // simplify the answer
            string assistantReply = "";
            foreach (var message in messagesJson.EnumerateArray())
            {
                if (message.GetProperty("role").GetString() == "assistant")
                {
                    assistantReply = message.GetProperty("content")[0].GetProperty("text").GetProperty("value").GetString();
                    break;
                }
            }

            // respond simplier respond
            return Ok(new { Theta = assistantReply });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = $"An error occurred: {ex.Message}" });
        }
    }
}
