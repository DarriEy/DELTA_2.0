import { renderHook, act } from '@testing-library/react';
import { useSpeechQueue } from '../useSpeechQueue';
import { describe, it, expect, vi } from 'vitest';

describe('useSpeechQueue', () => {
  it('should process text chunks into sentences', () => {
    const speak = vi.fn().mockResolvedValue();
    const { result } = renderHook(() => useSpeechQueue(speak));

    act(() => {
      result.current.processTextChunk('Hello world. This is a ');
    });

    expect(result.current.speechQueue).toContain('Hello world.');
    
    act(() => {
      result.current.processTextChunk('test.');
    });

    expect(result.current.speechQueue).toContain('This is a test.');
  });

  it('should flush the buffer', () => {
    const speak = vi.fn().mockResolvedValue();
    const { result } = renderHook(() => useSpeechQueue(speak));

    act(() => {
      result.current.processTextChunk('Unfinished sentence');
      result.current.flushBuffer();
    });

    expect(result.current.speechQueue).toContain('Unfinished sentence');
  });

  it('should clear the queue', () => {
    const speak = vi.fn().mockResolvedValue();
    const { result } = renderHook(() => useSpeechQueue(speak));

    act(() => {
      result.current.processTextChunk('Sentence 1. Sentence 2.');
      result.current.clearQueue();
    });

    expect(result.current.speechQueue).toHaveLength(0);
  });
});
