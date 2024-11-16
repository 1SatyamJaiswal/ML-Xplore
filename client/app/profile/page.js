"use client";
import { useEffect, useState } from "react";
import axios from "axios";
import Cookies from "js-cookie";
import Navbar from "../components/Navbar";
import { useRouter } from "next/navigation";

export default function ProfilePage() {
  const [userData, setUserData] = useState(null);
  const [userHistory, setUserHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const token = Cookies.get("token");
    if (!token) {
      router.push("/login"); // Redirect to login if no token is found
    } else {
      // Fetch user profile data after ensuring the user is authenticated
      fetchUserProfile();
      fetchUserHistory();
    }
  }, [router]);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/user`,
        {
          headers: {
            Authorization: `Bearer ${Cookies.get("token")}`,
          },
        }
      );
      setUserData(response.data); // Assuming the response contains name, email, and preferences
      setLoading(false);
    } catch (error) {
      console.error("Error fetching profile:", error);
      setError("Failed to load profile");
      setLoading(false);
    }
  };

  const fetchUserHistory = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/history`,
        {
          headers: {
            Authorization: `Bearer ${Cookies.get("token")}`,
          },
        }
      );
      setUserHistory(response.data); // Assuming the response contains user history
      setLoading(false);
    } catch (error) {
      console.error("Error fetching user history:", error);
      setError("Failed to load user history");
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-black dark:text-white transition-colors duration-300">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <h1 className="text-4xl font-bold text-center mb-8 dark:text-white">
            Profile
          </h1>

          <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              User Information
            </h2>

            <div className="space-y-4">
              <div>
                <p className="text-lg font-medium text-gray-600 dark:text-gray-300">
                  <span className="font-bold">Name:</span> {userData.name}
                </p>
              </div>

              <div>
                <p className="text-lg font-medium text-gray-600 dark:text-gray-300">
                  <span className="font-bold">Email:</span> {userData.email}
                </p>
              </div>

              <div>
                <div className="text-lg font-medium text-gray-600 dark:text-gray-300">
                  <span className="font-bold">Preferences:</span>
                  {userData.preferences.length > 0 ? (
                    <ul className="list-disc pl-5">
                      {userData.preferences.split(",").map((pref, index) => (
                        <li key={index}>{pref}s</li>
                      ))}
                    </ul>
                  ) : (
                    <span className="text-gray-500">No preferences set.</span>
                  )}
                </div>
              </div>
            </div>

            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-4">
              User History
            </h2>

            <div className="space-y-4">
              {userHistory.length > 0 ? (
                <ul>
                  {userHistory.map((item, index) => (
                    <li
                      key={index}
                      className="text-lg font-medium text-gray-600 dark:text-gray-300"
                    >
                      <a href={item} target="_blank" rel="noreferrer">
                        {item}
                      </a>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-lg font-medium text-gray-600 dark:text-gray-300">
                  No history found.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
