using Microsoft.AspNetCore.Mvc;
using OpenAI;
using OpenAI.Chat;
using iText.Kernel.Pdf;
using iText.Kernel.Pdf.Canvas.Parser;
using System.Text;

namespace SalesAssistantAPI.Controllers;

[Route("api/sales")]
[ApiController]
public class SalesAssistantController : ControllerBase
{
    private readonly ChatClient _chatClient;
    private readonly string _allDocuments;
    // private readonly string _productInfo;

    public SalesAssistantController()
    {
        // Initialize ChatClient with model and API key
        _chatClient = new ChatClient(
            model: "gpt-4",
            apiKey: Environment.GetEnvironmentVariable("OPENAI_API_KEY") ?? "sk-svcacct-CgWgSOj2RTUOUHIOIZF2wAOFcNVR0r9IMHNppVUFI5LMfOPH9qIu3IV5ha1XovSWNqyno8ST3BlbkFJ7Bdh93_ZqTraoRPU3Tv-R0y7gjVcpZNEg45sOwz-i47FIkBhugYsRZ1G2Ml7Ana_bPtIMAA"
        );

        // Load product information from PDF
        var pdfFiles = Directory.GetFiles("Resources", "*.pdf"); 
        
        _allDocuments = ExtractTextFromMultiplePdfs(pdfFiles);
    }

    //read multipule PDF
    private static string ExtractTextFromMultiplePdfs(string[] pdfPaths)
    {
        var text = new StringBuilder();

        foreach (var pdfPath in pdfPaths)
        {
            if (!System.IO.File.Exists(pdfPath))
            {
                text.AppendLine($"[Warning] {pdfPath} not found.\n");
                continue;
            }

              text.AppendLine($"\n Document: {Path.GetFileName(pdfPath)}\n");

            using (var pdfReader = new PdfReader(pdfPath))
            using (var pdfDocument = new PdfDocument(pdfReader))
            {
                for (int i = 1; i <= pdfDocument.GetNumberOfPages(); i++)
                {
                    var page = pdfDocument.GetPage(i);
                    text.AppendLine(PdfTextExtractor.GetTextFromPage(page));
                }
            }
        }

        return text.ToString();
    }

    // Handle user questions through Get endpoint
    [HttpGet("ask")]
    public IActionResult AskQuestion([FromQuery] string question)
    {
        if (string.IsNullOrEmpty(question))
        {
            return BadRequest(new { error = "Question cannot be empty." });
        }

        try
        {
            // Create system and user messages with explicit type
            ChatMessage[] messages = new ChatMessage[]
            {
                new SystemChatMessage($"You are a knowledgeable assistant. Below is important company information, including product details, refund policies, and general policies:\n{_allDocuments}"),
                new UserChatMessage(question)
            };

            // Get chat completion
            ChatCompletion completion = _chatClient.CompleteChat(messages);
            
            if (completion?.Content != null && completion.Content.Count > 0)
            {
                return Ok(new { Theta = completion.Content[0].Text });
            }

            return BadRequest(new { error = "Could not get a response." });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = $"An error occurred: {ex.Message}"});
        }
    }
}