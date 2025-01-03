"use client";
import { useEffect, useState } from "react";
import SearchBar from "./components/SearchBar";
import SearchResult from "./components/SearchResult";
import axios from "axios";
import Navbar from "./components/Navbar";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [email, setEmail] = useState("");
  const [id, setId] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [search, setSearch] = useState(false);
  const [selectedTags, setSelectedTags] = useState([]); // Track selected tags for filtering
  const router = useRouter();

  // Fetch search results when query or tags change
  const handleSearch = async (query) => {
    const effectiveQuery = query || "";
    
    try {
      if (!effectiveQuery && selectedTags.length === 0) {
        // If no query and no tags, fetch recommendations
        fetchRecommendations(id);
        setSearch(false);
        return;
      }

      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/search`,
        {
          params: {
            query: effectiveQuery,
            tags: selectedTags,  // Include the selected tags for filtering
          },
        }
      );
      setSearchResults(response.data);
      setSearch(true);
    } catch (error) {
      console.error("Error fetching search results:", error);
      setSearchResults([]); // Handle error gracefully by clearing results
    }
  };

  // Trigger search when tags change
  useEffect(() => {
    handleSearch(searchQuery);
  }, [selectedTags]);

  useEffect(() => {
    const token = Cookies.get("token");
    const user = Cookies.get("user");
    if (token && user) {
      const user_info = user.split(",");
      setEmail(user_info[1]);
      setId(user_info[0]);

      fetchRecommendations(user_info[0]);
    } else {
      router.push("/login"); // Redirect to login if no token is found
    }
  }, []); // Empty dependency array means this effect runs only once on mount

  const fetchRecommendations = async (id) => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/resources`, 
        {
          params: {
            user_id: id,  // Pass user_id as a query parameter
          },
          headers: {
            Authorization: `Bearer ${Cookies.get("token")}`,
            'Content-Type': 'application/json',  // Correct header name
          },
        }
      );
      setSearchResults(response.data);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      setSearchResults([]); // Handle error gracefully by clearing results
    }
  };

  // Handle change in tag selection
  const handleTagChange = (event) => {
    const { value, checked } = event.target;
    setSelectedTags((prevTags) =>
      checked ? [...prevTags, value] : prevTags.filter((tag) => tag !== value)
    );
  };

  // Tag configuration for easier management
  const TAG_OPTIONS = [
    { value: "dataset", label: "Dataset" },
    { value: "model", label: "Model" },
    { value: "article", label: "Article" },
    { value: "research paper", label: "Research Paper" }
  ];

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

          {/* Improved Tag Filters */}
          <div className="mb-8">
            <h2 className="text-lg font-medium mb-4">Filter by Tags</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {TAG_OPTIONS.map((tag) => (
                <label 
                  key={tag.value} 
                  className="flex items-center space-x-2 bg-white dark:bg-gray-800 p-2 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <input
                    type="checkbox"
                    value={tag.value}
                    checked={selectedTags.includes(tag.value)}
                    onChange={handleTagChange}
                    className="form-checkbox text-blue-600 dark:text-blue-500 focus:ring-blue-500"
                  />
                  <span className="text-gray-700 dark:text-gray-300">{tag.label}</span>
                </label>
              ))}
            </div>
          </div>

          {searchResults.length > 0 && (
            <div className="mt-6">
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                {search ? `Search Results: ${searchResults.length} found` : "Recommendations"}
              </p>
              <ul>
                {searchResults.map((result) => (
                  <SearchResult key={result.url} result={result} id={id} />
                ))}
              </ul>
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