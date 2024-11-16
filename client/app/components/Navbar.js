"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";

export default function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const router = useRouter();

  useEffect(() => {
    const token = Cookies.get("token");
    if (token) {
      setIsLoggedIn(true);
    }
    const darkMode = localStorage.getItem("darkMode");
    if (darkMode) {
      setDarkMode(darkMode);
      document.documentElement.classList.add("dark");
    }
  }, []);

  const handleLogout = () => {
    Cookies.remove("token");
    Cookies.remove("user");
    setIsLoggedIn(false);
  };

  const handleProfileClick = () => {
    router.push("/profile");
    console.log("Profile clicked");
  };

  const handleLogin = () => {
    router.push("/login");
    setIsLoggedIn(true);
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    localStorage.setItem("darkMode", !darkMode);
    if (!darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 flex items-center space-x-2">
      {/* Profile Icon */}
      <button
        onClick={toggleDarkMode}
        className="bg-gray-200 dark:bg-gray-700 p-2 rounded-full hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        title="Toggle Dark Mode"
      >
        {darkMode ? "☀️" : "🌙"}
      </button>
      {isLoggedIn ? (
        <>
          <button
            onClick={handleProfileClick}
            className="bg-gray-200 dark:bg-gray-700 p-2 rounded-full hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            title="Profile"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-gray-600 dark:text-gray-300"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </button>

          {/* Logout Icon */}
          <button
            onClick={handleLogout}
            className="bg-gray-200 dark:bg-gray-700 p-2 rounded-full hover:bg-red-100 dark:hover:bg-red-900 transition-colors"
            title="Logout"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-red-600 dark:text-red-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
          </button>
        </>
      ) : (
        <button
          onClick={handleLogin}
          className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition-colors"
        >
          Login
        </button>
      )}
    </div>
  );
}
