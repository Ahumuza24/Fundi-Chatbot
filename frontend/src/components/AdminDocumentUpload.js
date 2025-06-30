import React, { useState, useRef } from 'react';
import { X, Upload, FileText, AlertCircle, CheckCircle, Trash2 } from 'lucide-react';
import api from '../utils/axios';

function AdminDocumentUpload() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadProgress, setUploadProgress] = useState({});
  const fileInputRef = useRef(null);

  const getErrorMessage = (error) => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    
    if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
      return 'Unable to connect to the server. Please check your connection and try again.';
    }
    
    if (error.response?.status === 500) {
      return 'Server error. Please try again later.';
    }
    
    if (error.response?.status === 401) {
      return 'Authentication failed. Please log in again.';
    }
    
    if (error.response?.status === 413) {
      return 'File is too large. Please choose a smaller file.';
    }
    
    return 'Upload failed. Please try again.';
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    const validFiles = [];
    const invalidFiles = [];

    files.forEach(file => {
      // Validate file type
      const validTypes = ['.pdf', '.docx'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!validTypes.includes(fileExtension)) {
        invalidFiles.push(`${file.name} - Invalid file type`);
        return;
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        invalidFiles.push(`${file.name} - File too large (max 10MB)`);
        return;
      }

      validFiles.push(file);
    });

    if (invalidFiles.length > 0) {
      setUploadStatus({
        type: 'error',
        message: `Invalid files:\n${invalidFiles.join('\n')}`
      });
    }

    setSelectedFiles(prev => [...prev, ...validFiles]);
    setUploadStatus(null);
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setUploadStatus(null);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setUploadStatus(null);
    setUploadProgress({});

    const results = [];
    let successCount = 0;
    let errorCount = 0;

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      
      try {
        setUploadProgress(prev => ({ ...prev, [file.name]: 'uploading' }));
        
        const formData = new FormData();
        formData.append('file', file);

        await api.post('/documents/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000, // 60 second timeout for large files
        });

        setUploadProgress(prev => ({ ...prev, [file.name]: 'success' }));
        results.push({ file: file.name, status: 'success' });
        successCount++;
      } catch (error) {
        console.error(`Upload error for ${file.name}:`, error);
        setUploadProgress(prev => ({ ...prev, [file.name]: 'error' }));
        results.push({ file: file.name, status: 'error', error: getErrorMessage(error) });
        errorCount++;
      }
    }

    setUploading(false);

    if (successCount > 0 && errorCount === 0) {
      setUploadStatus({
        type: 'success',
        message: `All ${successCount} document(s) uploaded successfully!`
      });
      setSelectedFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } else if (successCount > 0 && errorCount > 0) {
      setUploadStatus({
        type: 'warning',
        message: `${successCount} document(s) uploaded successfully, ${errorCount} failed.`
      });
    } else {
      setUploadStatus({
        type: 'error',
        message: `Failed to upload ${errorCount} document(s).`
      });
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const files = Array.from(event.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect({ target: { files } });
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'uploading':
        return <div className="h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      default:
        return null;
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900">Upload Documents</h3>
        <button 
          onClick={handleUpload}
          disabled={uploading || selectedFiles.length === 0}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Upload className="h-4 w-4 mr-2" />
          {uploading ? 'Uploading...' : `Upload ${selectedFiles.length} File(s)`}
        </button>
      </div>

      {/* Upload area */}
      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors mb-6"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          <label htmlFor="file-upload" className="cursor-pointer">
            <span className="mt-2 block text-sm font-medium text-gray-900">
              Drop files here or click to browse
            </span>
            <span className="mt-1 block text-xs text-gray-500">
              PDF or DOCX files only, max 10MB each
            </span>
          </label>
          <input
            id="file-upload"
            ref={fileInputRef}
            name="file-upload"
            type="file"
            multiple
            className="sr-only"
            accept=".pdf,.docx"
            onChange={handleFileSelect}
          />
        </div>
      </div>

      {/* Status message */}
      {uploadStatus && (
        <div className={`mb-6 p-4 rounded-lg flex items-center ${
          uploadStatus.type === 'success' 
            ? 'bg-green-50 text-green-800' 
            : uploadStatus.type === 'warning'
            ? 'bg-yellow-50 text-yellow-800'
            : 'bg-red-50 text-red-800'
        }`}>
          {uploadStatus.type === 'success' ? (
            <CheckCircle className="h-5 w-5 mr-2" />
          ) : uploadStatus.type === 'warning' ? (
            <AlertCircle className="h-5 w-5 mr-2" />
          ) : (
            <AlertCircle className="h-5 w-5 mr-2" />
          )}
          <span className="text-sm whitespace-pre-line">{uploadStatus.message}</span>
        </div>
      )}

      {/* Selected files */}
      {selectedFiles.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h4 className="text-sm font-medium text-gray-900">Selected Files ({selectedFiles.length})</h4>
          </div>
          <ul className="divide-y divide-gray-200">
            {selectedFiles.map((file, index) => (
              <li key={index} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FileText className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{file.name}</p>
                      <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {uploadProgress[file.name] && getStatusIcon(uploadProgress[file.name])}
                    <button
                      onClick={() => removeFile(index)}
                      className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                      title="Remove file"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default AdminDocumentUpload; 