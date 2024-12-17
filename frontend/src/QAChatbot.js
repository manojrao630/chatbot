import React, { useState } from 'react';
import { FileTextIcon, SendIcon } from 'lucide-react';

const QAChatbot = () => {
  const [file, setFile] = useState(null);
  const [context, setContext] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState('');

  const handleFileUpload = async (event) => {
    const uploadedFile = event.target.files[0];
    setFile(uploadedFile);
    
    if (uploadedFile) {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      try {
        const response = await fetch('http://localhost:5000/upload', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error('File upload failed');
        }

        const data = await response.json();
        setContext(data.context);
        setError('');
      } catch (err) {
        setError('Failed to upload file');
        console.error(err);
      }
    }
  };

  const handleAskQuestion = async () => {
    if (!context || !question) {
      setError('Please upload a file and enter a question');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ context, question })
      });

      if (!response.ok) {
        throw new Error('Question answering failed');
      }

      const data = await response.json();
      setAnswer(data.answer);
      setError('');
    } catch (err) {
      setError('Failed to get answer');
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white shadow-md rounded-lg p-6 w-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-4 text-center text-gray-800">
          Q&A Chatbot
        </h1>

        {/* File Upload */}
        <div className="mb-4">
          <label 
            htmlFor="file-upload" 
            className="flex items-center justify-center w-full p-4 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition"
          >
            <FileTextIcon className="mr-2 text-gray-600" />
            <span className="text-gray-600">
              {file ? file.name : 'Upload TXT/PDF File'}
            </span>
            <input 
              id="file-upload"
              type="file" 
              accept=".txt,.pdf"
              className="hidden"
              onChange={handleFileUpload}
            />
          </label>
        </div>

        {/* Context Preview */}
        {context && (
          <div className="mb-4">
            <textarea 
              className="w-full p-2 border rounded-lg bg-gray-50 text-sm h-32"
              value={context}
              readOnly
              placeholder="Document context"
            />
          </div>
        )}

        {/* Question Input */}
        <div className="mb-4 flex">
          <input 
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about the document"
            className="flex-grow p-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button 
            onClick={handleAskQuestion}
            className="bg-blue-500 text-white p-2 rounded-r-lg hover:bg-blue-600 transition flex items-center"
          >
            <SendIcon className="mr-1" size={20} />
            Ask
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            {error}
          </div>
        )}

        {/* Answer Display */}
        {answer && (
          <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg">
            <h3 className="font-bold text-green-800 mb-2">Answer:</h3>
            <p className="text-green-700">{answer}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default QAChatbot;