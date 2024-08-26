import { useState, useEffect } from 'react';
import axios from 'axios';

function TourAnalytics() {
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/tour/analytics/')
        setAnalytics(res.data)
      } catch (error) {
        console.error('Error fetching analytics:', error.response?.data?.error || error.message)
      }
    };
    fetchAnalytics();
  }, []);

  if (!analytics) return <div>Loading analytics...</div>;

  return (
    <div className="tour-analytics">
      <h2>Tour Analytics</h2>
      <ul>
        <li>Total Users: {analytics.total_users}</li>
        <li>Completed Tours: {analytics.completed_tours}</li>
        <li>Average Progress: {analytics.average_progress}%</li>
      </ul>
    </div>
  );
}

export default TourAnalytics;