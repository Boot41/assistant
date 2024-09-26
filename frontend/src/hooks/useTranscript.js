import { useState, useCallback, useMemo } from 'react';

export function useTranscript() {
  const [transcript, setTranscript] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  const addToTranscript = useCallback((speaker, text, timestamp) => {
    setTranscript(prevTranscript => [
      ...prevTranscript,
      { speaker, text, timestamp }
    ]);
  }, []);

  const clearTranscript = useCallback(() => {
    setTranscript([]);
  }, []);

  const getTranscriptAsJSON = useCallback(() => {
    return JSON.stringify(transcript);
  }, [transcript]);

  const filteredTranscript = useMemo(() => {
    return transcript.filter(entry => {
      const matchesSearch = entry.text.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesDateRange = (!startDate || entry.timestamp >= startDate) &&
                               (!endDate || entry.timestamp <= endDate);
      return matchesSearch && matchesDateRange;
    });
  }, [transcript, searchTerm, startDate, endDate]);

  const exportTranscript = useCallback(() => {
    const content = filteredTranscript.map(entry => 
      `${new Date(entry.timestamp).toLocaleString()} - ${entry.speaker}: ${entry.text}`
    ).join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'transcript.txt';
    link.click();
    URL.revokeObjectURL(url);
  }, [filteredTranscript]);

  return {
    transcript: filteredTranscript,
    addToTranscript,
    clearTranscript,
    getTranscriptAsJSON,
    setSearchTerm,
    setStartDate,
    setEndDate,
    exportTranscript
  };
}