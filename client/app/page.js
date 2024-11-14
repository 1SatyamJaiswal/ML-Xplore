"use client";
import { useState } from "react";
import SearchBar from "./components/SearchBar";
import SearchResult from "./components/SearchResult";
import { mockSearchResults } from "./utils/mockSearchData";
import Navbar from "./components/Navbar";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);

  const handleSearch = (query) => {
    if (!query) {
      setSearchResults([]);
      return;
    }

    // Simulate search with mock data
    const filteredResults = mockSearchResults.filter(
      (result) =>
        result.title.toLowerCase().includes(query.toLowerCase()) ||
        result.description.toLowerCase().includes(query.toLowerCase())
    );

    setSearchResults(filteredResults);
  };

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-black dark:text-white transition-colors duration-300">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <h1 className="text-4xl font-bold text-center mb-8 dark:text-white">
            ML-Xplore
          </h1>

          <div className="mb-8">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              onSearch={handleSearch}
            />
          </div>

          {searchResults.length > 0 && (
            <div className="mt-6">
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                {searchResults.length} results found
              </p>
              {searchResults.map((result) => (
                <SearchResult key={result.id} result={result} />
              ))}
            </div>
          )}

          {searchQuery && searchResults.length === 0 && (
            <div className="text-center text-gray-600 dark:text-gray-300">
              No results found for "{searchQuery}"
            </div>
          )}
        </div>
      </div>
    </>
  );
}
