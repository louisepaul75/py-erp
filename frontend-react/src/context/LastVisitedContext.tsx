'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation'; // Use next/navigation for App Router

const MAX_VISITED_ITEMS = 5; // Keep the last 5 visited items
const LOCAL_STORAGE_KEY = 'lastVisitedItems';

interface VisitedItem {
  type: string; // e.g., 'customer', 'product', 'order'
  id: string;
  name: string;
  path: string;
  timestamp: number; // For potential future use (e.g., sorting)
}

interface LastVisitedContextType {
  lastVisitedItems: VisitedItem[];
  addVisitedItem: (item: Omit<VisitedItem, 'timestamp'>) => void;
}

const LastVisitedContext = createContext<LastVisitedContextType | undefined>(undefined);

export const LastVisitedProvider = ({ children }: { children: ReactNode }) => {
  const [lastVisitedItems, setLastVisitedItems] = useState<VisitedItem[]>([]);
  const router = useRouter(); // Get router instance

  // Load initial state from localStorage
  useEffect(() => {
    try {
      const storedItems = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (storedItems) {
        setLastVisitedItems(JSON.parse(storedItems));
      }
    } catch (error) {
      console.error("Failed to load last visited items from localStorage:", error);
      // Optionally clear corrupted storage
      // localStorage.removeItem(LOCAL_STORAGE_KEY);
    }
  }, []);

  // Persist state to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(lastVisitedItems));
    } catch (error) {
      console.error("Failed to save last visited items to localStorage:", error);
    }
  }, [lastVisitedItems]);

  const addVisitedItem = useCallback((item: Omit<VisitedItem, 'timestamp'>) => {
    setLastVisitedItems(prevItems => {
      const newItem: VisitedItem = { ...item, timestamp: Date.now() };
      // Remove existing item with the same path to avoid duplicates and move it to the top
      const filteredItems = prevItems.filter(prevItem => prevItem.path !== newItem.path);
      // Add the new item to the beginning of the list
      const updatedItems = [newItem, ...filteredItems];
      // Limit the list size
      return updatedItems.slice(0, MAX_VISITED_ITEMS);
    });
  }, []); // No dependencies needed if setLastVisitedItems is stable

  return (
    <LastVisitedContext.Provider value={{ lastVisitedItems, addVisitedItem }}>
      {children}
    </LastVisitedContext.Provider>
  );
};

export const useLastVisited = (): LastVisitedContextType => {
  const context = useContext(LastVisitedContext);
  if (context === undefined) {
    throw new Error('useLastVisited must be used within a LastVisitedProvider');
  }
  return context;
}; 