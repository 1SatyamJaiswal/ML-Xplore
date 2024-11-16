"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import NavbarLogin from "../components/NavbarLogin";
import { toast } from "react-toastify";
import axios from "axios";
import { Toast, ToastContainer } from "react-toastify/dist/components";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [preferences, setPreferences] = useState([]);
  const router = useRouter();

  const preferenceOptions = [
    "Models",
    "Articles",
    "Research Papers",
    "Datasets",
  ];

  const handlePreferenceChange = (preference) => {
    if (preferences.includes(preference)) {
      setPreferences(preferences.filter((p) => p !== preference));
    } else {
      setPreferences([...preferences, preference]);
    }
  };

  const handleSubmit = async (e) => {
    // Basic validation
    if (!name || !email || !password || preferences.length === 0) {
      toast.error(
        "Please fill out all fields and select at least one preference."
      );
      return;
    }

    // Basic email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      toast.error("Please enter a valid email address.");
      return;
    }

    // Basic password length check
    if (password.length < 6) {
      toast.error("Password must be at least 6 characters long.");
      return;
    }

    // Mock registration (replace with actual API call later)
    try {
      const userData = {
        email,
        name,
        password,
        preferences,
      };
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/register`,
        userData
      );
      toast.success("Registration successful. Redirecting to login page...");
      router.push("/login");
    } catch (err) {
      toast.error("Registration failed. Please try again.");
      console.error("Registration failed:", err);
    }
  };

  return (
    <>
      <NavbarLogin />
      <ToastContainer />
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
        <div className="max-w-md w-full space-y-8 bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg">
          <div>
            <h2 className="text-center text-3xl font-extrabold text-gray-900 dark:text-white">
              Create your account
            </h2>
          </div>
          <div className="mt-8 space-y-6">
            <div className="rounded-md shadow-sm -space-y-px">
              <div>
                <label htmlFor="name" className="sr-only">
                  Name
                </label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border 
                border-gray-300 dark:border-gray-700 placeholder-gray-500 text-gray-900 
                dark:text-white dark:bg-gray-700 rounded-t-md focus:outline-none 
                focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Full name"
                />
              </div>
              <div>
                <label htmlFor="email" className="sr-only">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border 
                border-gray-300 dark:border-gray-700 placeholder-gray-500 text-gray-900 
                dark:text-white dark:bg-gray-700 focus:outline-none 
                focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Email address"
                />
              </div>
              <div>
                <label htmlFor="password" className="sr-only">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border 
                border-gray-300 dark:border-gray-700 placeholder-gray-500 text-gray-900 
                dark:text-white dark:bg-gray-700 rounded-b-md focus:outline-none 
                focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Password"
                />
              </div>
            </div>

            <div>
              <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Select your preferences (in order of importance):
              </p>
              <div className="mt-2 space-y-2">
                {preferenceOptions.map((option) => (
                  <div key={option} className="flex items-center">
                    <input
                      type="checkbox"
                      id={option}
                      value={option}
                      checked={preferences.includes(option)}
                      onChange={() => handlePreferenceChange(option)}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label
                      htmlFor={option}
                      className="ml-3 text-sm text-gray-700 dark:text-gray-300"
                    >
                      {option}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <button
                type="submit"
                onClick={handleSubmit}
                className="group relative w-full flex justify-center py-2 px-4 
              border border-transparent text-sm font-medium rounded-md text-white 
              bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 
              focus:ring-offset-2 focus:ring-blue-500"
              >
                Register
              </button>
            </div>
          </div>

          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Already have an account?{" "}
              <a href="/login" className="text-blue-600 hover:text-blue-500">
                Sign in
              </a>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
