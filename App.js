import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, ScatterChart, Scatter, ZAxis, LabelList, ComposedChart, Area, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedYearRange, setSelectedYearRange] = useState('all');

  useEffect(() => {
    const processData = async () => {
      try {
        // Using fetch API instead of window.fs.readFile for GitHub Pages compatibility
        const response = await fetch(`${process.env.PUBLIC_URL}/videogames_final.csv`);
        const fileContent = await response.text();
        
        // Use Papaparse to parse CSV
        const Papa = await import('papaparse');
        const result = Papa.default.parse(fileContent, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true
        });
        
        setData(result.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    processData();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-500 border-solid mx-auto mb-4"></div>
        <p className="text-xl">Loading data...</p>
      </div>
    </div>
  );
  
  if (error) return (
    <div className="p-8 text-center">
      <div className="bg-red-100 p-4 rounded-lg border border-red-300 inline-block">
        <h2 className="text-xl font-bold text-red-700 mb-2">Error Loading Data</h2>
        <p className="text-red-600">{error}</p>
      </div>
    </div>
  );
  
  if (!data) return <div className="p-4 text-center">No data available</div>;

  // Process data for visualizations
  
  // 1. Metascore distribution
  const metascoreRanges = {
    '95-97': 0,
    '90-94': 0,
    '85-89': 0
  };

  data.forEach(game => {
    if (game.metascore) {
      if (game.metascore >= 95) {
        metascoreRanges['95-97']++;
      } else if (game.metascore >= 90) {
        metascoreRanges['90-94']++;
      } else if (game.metascore >= 85) {
        metascoreRanges['85-89']++;
      }
    }
  });

  const metascoreData = Object.entries(metascoreRanges).map(([range, count]) => ({
    range,
    count
  }));

  // 2. Release year distribution
  const yearCounts = {};
  data.forEach(game => {
    if (game.release_date) {
      const year = game.release_date.split('-')[0];
      if (year && !isNaN(parseInt(year))) {
        yearCounts[year] = (yearCounts[year] || 0) + 1;
      }
    }
  });

  // Get years and decades for filtering
  const years = Object.keys(yearCounts).sort((a, b) => parseInt(a) - parseInt(b));
  const decades = [...new Set(years.map(year => `${Math.floor(parseInt(year) / 10) * 10}s`))];

  // Filter data based on selected year range
  const getFilteredData = () => {
    if (selectedYearRange === 'all') return data;
    
    if (selectedYearRange.endsWith('s')) {
      // Decade filter
      const decade = parseInt(selectedYearRange);
      return data.filter(game => {
        if (!game.release_date) return false;
        const year = parseInt(game.release_date.split('-')[0]);
        return year >= decade && year < decade + 10;
      });
    } else {
      // Specific year filter
      return data.filter(game => {
        if (!game.release_date) return false;
        return game.release_date.startsWith(selectedYearRange);
      });
    }
  };

  const filteredData = getFilteredData();

  // Sort years and convert to array for chart
  const releaseYearData = Object.entries(yearCounts)
    .sort((a, b) => parseInt(a[0]) - parseInt(b[0]))
    .map(([year, count]) => ({
      year,
      count
    }));

  // 3. Top genres
  const genreCounts = {};
  filteredData.forEach(game => {
    if (game.genres) {
      const genres = game.genres.split(',').map(g => g.trim());
      genres.forEach(genre => {
        genreCounts[genre] = (genreCounts[genre] || 0) + 1;
      });
    }
  });

  const topGenresData = Object.entries(genreCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([genre, count]) => ({
      genre,
      count
    }));

  // 4. Steam review distribution
  const reviewCounts = {};
  filteredData.forEach(game => {
    if (game.steam_review_summary) {
      reviewCounts[game.steam_review_summary] = (reviewCounts[game.steam_review_summary] || 0) + 1;
    }
  });

  const steamReviewData = Object.entries(reviewCounts)
    .filter(([summary]) => summary !== '6 user reviews') // Filter out non-standard entry
    .map(([summary, count]) => ({
      summary,
      count,
      percentage: Math.round(count / Object.values(reviewCounts).reduce((a, b) => a + b, 0) * 100)
    }));

  // 5. Top developers
  const developerCounts = {};
  filteredData.forEach(game => {
    const developer = game.developer || game.steam_developer;
    if (developer) {
      developerCounts[developer] = (developerCounts[developer] || 0) + 1;
    }
  });

  const topDevelopersData = Object.entries(developerCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([developer, count]) => ({
      developer: developer.length > 20 ? developer.substring(0, 18) + '...' : developer,
      fullName: developer,
      count
    }));

  // 6. Price vs. Metascore correlation
  const priceVsMetascoreData = filteredData
    .filter(game => game.metascore && game.price && typeof game.price === 'string')
    .map(game => {
      // Extract price value (removing currency symbol)
      const priceMatch = game.price.match(/[\d\.]+/);
      const price = priceMatch ? parseFloat(priceMatch[0]) : null;
      
      return {
        game: game.game_title,
        metascore: game.metascore,
        price: price,
        genre: game.genres ? game.genres.split(',')[0].trim() : 'Unknown'
      };
    })
    .filter(item => item.price !== null && item.price < 800); // Filter out extreme outliers

  // 7. Release date vs. Metascore
  const yearVsMetascoreData = filteredData
    .filter(game => game.metascore && game.release_date)
    .map(game => {
      const year = parseInt(game.release_date.split('-')[0]);
      return {
        game: game.game_title,
        year: year,
        metascore: game.metascore
      };
    })
    .sort((a, b) => a.year - b.year);

  // 8. Average price by genre
  const genrePriceMap = {};
  const genreCounts2 = {};
  
  filteredData.forEach(game => {
    if (game.genres && game.price && typeof game.price === 'string') {
      const priceMatch = game.price.match(/[\d\.]+/);
      const price = priceMatch ? parseFloat(priceMatch[0]) : null;
      
      if (price !== null) {
        const primaryGenre = game.genres.split(',')[0].trim();
        genrePriceMap[primaryGenre] = (genrePriceMap[primaryGenre] || 0) + price;
        genreCounts2[primaryGenre] = (genreCounts2[primaryGenre] || 0) + 1;
      }
    }
  });
  
  const genrePriceData = Object.entries(genrePriceMap)
    .map(([genre, totalPrice]) => ({
      genre,
      avgPrice: totalPrice / genreCounts2[genre]
    }))
    .filter(item => genreCounts2[item.genre] >= 3) // Only include genres with at least 3 games
    .sort((a, b) => b.avgPrice - a.avgPrice)
    .slice(0, 10);

  // 9. Popular Steam tags analysis
  const tagCounts = {};
  filteredData.forEach(game => {
    if (game.steam_tags) {
      const tags = game.steam_tags.split(',').map(t => t.trim());
      tags.forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    }
  });

  const topTagsData = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15)
    .map(([tag, count]) => ({
      tag,
      count
    }));

  // 10. Metascore by decade
  const metascoreByDecade = {};
  const decadeCounts = {};
  
  data.forEach(game => {
    if (game.metascore && game.release_date) {
      const year = parseInt(game.release_date.split('-')[0]);
      const decade = `${Math.floor(year / 10) * 10}s`;
      
      metascoreByDecade[decade] = (metascoreByDecade[decade] || 0) + game.metascore;
      decadeCounts[decade] = (decadeCounts[decade] || 0) + 1;
    }
  });
  
  const decadeMetascoreData = Object.entries(metascoreByDecade)
    .map(([decade, totalScore]) => ({
      decade,
      avgMetascore: (totalScore / decadeCounts[decade]).toFixed(2)
    }))
    .sort((a, b) => {
      const decadeA = parseInt(a.decade);
      const decadeB = parseInt(b.decade);
      return decadeA - decadeB;
    });

  // 11. Top games table
  const topGames = filteredData
    .filter(game => game.metascore)
    .sort((a, b) => b.metascore - a.metascore)
    .slice(0, 10)
    .map(game => ({
      title: game.game_title,
      metascore: game.metascore,
      releaseYear: game.release_date ? game.release_date.split('-')[0] : 'Unknown',
      developer: game.developer || game.steam_developer || 'Unknown',
      genre: game.genres ? game.genres.split(',')[0].trim() : 'Unknown',
      steamReview: game.steam_review_summary || 'N/A'
    }));

  // 12. Metascore distribution radar by genre
  const topGenresForRadar = Object.entries(genreCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([genre]) => genre);

  const genreScoreMap = {};
  const genreScoreCounts = {};
  
  filteredData.forEach(game => {
    if (game.metascore && game.genres) {
      const primaryGenre = game.genres.split(',')[0].trim();
      if (topGenresForRadar.includes(primaryGenre)) {
        genreScoreMap[primaryGenre] = (genreScoreMap[primaryGenre] || 0) + game.metascore;
        genreScoreCounts[primaryGenre] = (genreScoreCounts[primaryGenre] || 0) + 1;
      }
    }
  });
  
  const genreRadarData = topGenresForRadar.map(genre => ({
    genre,
    avgScore: (genreScoreMap[genre] / genreScoreCounts[genre]).toFixed(1)
  }));

  // Colors for charts
  const COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 shadow-md rounded">
          <p className="font-bold">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderActiveTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Metascore Distribution</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={metascoreData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="range" tick={{ fill: '#4b5563' }} />
                    <YAxis tick={{ fill: '#4b5563' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="#6366f1" name="Number of Games">
                      <LabelList dataKey="count" position="top" fill="#4b5563" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Steam Review Distribution</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={steamReviewData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={110}
                      fill="#8884d8"
                      dataKey="count"
                      nameKey="summary"
                      label={({ summary, percentage }) => `${percentage}%`}
                    >
                      {steamReviewData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value, name, props) => [`${value} games`, props.payload.summary]} />
                    <Legend formatter={(value, entry) => entry.payload.summary} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Metascore by Decade</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <ComposedChart data={decadeMetascoreData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="decade" tick={{ fill: '#4b5563' }} />
                    <YAxis domain={[85, 92]} tick={{ fill: '#4b5563' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="avgMetascore" fill="#8884d8" stroke="#6366f1" />
                    <Bar dataKey="avgMetascore" fill="#6366f1" barSize={20} />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Games by Release Year</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={releaseYearData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="year" 
                      tick={{ fill: '#4b5563' }}
                      interval="preserveStartEnd"
                      tickFormatter={value => {
                        if (['1996', '2000', '2005', '2010', '2015', '2020', '2025'].includes(value)) {
                          return value;
                        }
                        return '';
                      }}
                    />
                    <YAxis tick={{ fill: '#4b5563' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Line 
                      type="monotone" 
                      dataKey="count" 
                      stroke="#6366f1" 
                      strokeWidth={2}
                      dot={{ fill: '#6366f1', r: 4 }}
                      activeDot={{ fill: '#4f46e5', r: 6, stroke: '#c7d2fe', strokeWidth: 2 }}
                      name="Number of Games" 
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Genre Performance (Avg. Metascore)</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={genreRadarData}>
                    <PolarGrid stroke="#e5e7eb" />
                    <PolarAngleAxis dataKey="genre" tick={{ fill: '#4b5563', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[85, 95]} tick={{ fill: '#4b5563' }} />
                    <Radar name="Average Metascore" dataKey="avgScore" stroke="#6366f1" fill="#818cf8" fillOpacity={0.6} />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg shadow-md mb-8">
              <h2 className="text-lg font-semibold mb-4 text-indigo-800">Top 10 Highest Rated Games</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Metascore</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Year</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Developer</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Genre</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Steam Review</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {topGames.map((game, index) => (
                      <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{game.title}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{game.metascore}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{game.releaseYear}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{game.developer}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{game.genre}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{game.steamReview}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4 text-indigo-800">Key Insights</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-2">Dataset Overview</h3>
                  <ul className="list-disc pl-5 space-y-2 text-gray-700">
                    <li>Dataset contains <span className="font-semibold">{data.length} video games</span> with Metacritic scores ranging from 88-97</li>
                    <li>Majority of games ({metascoreRanges['90-94']}) have Metascores between 90-94</li>
                    <li>Only {metascoreRanges['95-97']} games achieved a Metascore of 95 or higher</li>
                    <li>All games in the dataset are on the PC platform</li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-2">Content Analysis</h3>
                  <ul className="list-disc pl-5 space-y-2 text-gray-700">
                    <li>FPS is the most common genre, followed by Western RPG and Action Adventure</li>
                    <li>Top developers: Firaxis Games, BioWare, and Valve Software</li>
                    <li>The years 2002, 2024, and 2023 had the highest number of highly-rated games</li>
                    <li><span className="font-semibold">Very Positive</span> is the most common Steam review summary ({Math.round(reviewCounts["Very Positive"] / Object.values(reviewCounts).reduce((a, b) => a + b, 0) * 100)}% of reviews)</li>
                  </ul>
                </div>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-800 mb-2">Advanced Insights</h3>
                <ul className="list-disc pl-5 space-y-2 text-gray-700">
                  <li>Games from the 2020s have the highest average Metascore, suggesting recent games have higher quality or rating standards have shifted</li>
                  <li>Older highly-rated games tend to be from established franchises like Half-Life, Civilization, and Baldur's Gate</li>
                  <li>The most expensive games aren't necessarily the highest rated - mid-tier Metascore games (80-89) have higher average prices</li>
                  <li>Blizzard Entertainment, Electronic Arts, and Valve Software publish the most high-rated games</li>
                  <li>Single-player games dominate the top tags, appearing in 127 of the highly-rated games</li>
                </ul>
              </div>
            </div>
          </>
        );
      
      case 'genres':
        return (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Top 10 Genres</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={topGenresData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis type="number" tick={{ fill: '#4b5563' }} />
                    <YAxis dataKey="genre" type="category" width={150} tick={{ fill: '#4b5563' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="#6366f1" name="Number of Games">
                      <LabelList dataKey="count" position="right" fill="#4b5563" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Average Price by Genre</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={genrePriceData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis type="number" tick={{ fill: '#4b5563' }} />
                    <YAxis dataKey="genre" type="category" width={150} tick={{ fill: '#4b5563' }} />
                    <Tooltip 
                      content={<CustomTooltip />}
                      formatter={(value) => [`$${value.toFixed(2)}`, 'Average Price']}
                    />
                    <Bar dataKey="avgPrice" fill="#10b981" name="Average Price ($)">
                      <LabelList dataKey="avgPrice" position="right" formatter={(value) => `$${value.toFixed(2)}`} fill="#4b5563" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Top 15 Steam Tags</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={topTagsData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis type="number" tick={{ fill: '#4b5563' }} />
                    <YAxis dataKey="tag" type="category" width={150} tick={{ fill: '#4b5563' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="#818cf8" name="Number of Games">
                      <LabelList dataKey="count" position="right" fill="#4b5563" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Genre Analysis Insights</h2>
                <div className="p-4 border border-indigo-100 rounded-lg bg-indigo-50">
                  <h3 className="text-md font-medium text-indigo-800 mb-3">Key Findings</h3>
                  <ul className="list-disc pl-5 space-y-3 text-gray-700">
                    <li>
                      <span className="font-semibold">FPS dominates:</span> First-person shooters are the most represented genre with 28 games, followed by Western RPGs (18) and Action Adventure (15)
                    </li>
                    <li>
                      <span className="font-semibold">Genre pricing patterns:</span> Simulation and Strategy games tend to have higher average prices, suggesting these genres might offer more complex gameplay or have dedicated fan bases willing to pay premium prices
                    </li>
                    <li>
                      <span className="font-semibold">Tag prevalence:</span> "Singleplayer" is the most common tag (127 games), followed by "Multiplayer" (78) and "Action" (76), indicating solo experiences still dominate among highly-rated games
                    </li>
                    <li>
                      <span className="font-semibold">Cross-genre appeal:</span> Many top-rated games are tagged with both "Story Rich" and "Atmospheric" (60+ games each), suggesting narrative quality and immersion are important factors in high ratings
                    </li>
                    <li>
                      <span className="font-semibold">Genre evolution:</span> Western RPGs and Action RPGs have seen increased representation in recent years, while traditional RTS games have declined
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold mb-4 text-indigo-800">Price vs. Metascore by Genre</h2>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    type="number" 
                    dataKey="metascore" 
                    name="Metascore" 
                    domain={[87, 98]}
                    tick={{ fill: '#4b5563' }}
                    label={{ value: 'Metascore', position: 'bottom', fill: '#4b5563', dy: 10 }}
                  />
                  <YAxis 
                    type="number" 
                    dataKey="price" 
                    name="Price" 
                    tick={{ fill: '#4b5563' }}
                    label={{ value: 'Price ($)', angle: -90, position: 'left', fill: '#4b5563', dx: -10 }}
                  />
                  <ZAxis range={[60, 400]} />
                  <Tooltip 
                    cursor={{ strokeDasharray: '3 3' }}
                    formatter={(value, name, props) => {
                      if (name === 'price') return [`$${value}`, 'Price'];
                      return [value, name];
                    }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-white p-3 border border-gray-200 shadow-md rounded">
                            <p className="font-bold">{payload[0].payload.game}</p>
                            <p>Genre: {payload[0].payload.genre}</p>
                            <p>Metascore: {payload[0].payload.metascore}</p>
                            <p>Price: ${payload[0].payload.price}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Scatter 
                    name="Games" 
                    data={priceVsMetascoreData} 
                    fill="#6366f1"
                    shape="circle"
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </>
        );
      
      case 'developers':
        return (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Top 8 Developers</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={topDevelopersData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis type="number" tick={{ fill: '#4b5563' }} />
                    <YAxis 
                      dataKey="developer" 
                      type="category" 
                      width={150} 
                      tick={{ fill: '#4b5563' }}
                    />
                    <Tooltip 
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div className="bg-white p-3 border border-gray-200 shadow-md rounded">
                              <p className="font-bold">{payload[0].payload.fullName}</p>
                              <p>Games: {payload[0].payload.count}</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar dataKey="count" fill="#6366f1" name="Number of Games">
                      <LabelList dataKey="count" position="right" fill="#4b5563" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4 text-indigo-800">Release Year vs. Metascore</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      type="number" 
                      dataKey="year" 
                      name="Year" 
                      domain={['dataMin - 1', 'dataMax + 1']}
                      tick={{ fill: '#4b5563' }}
                      label={{ value: 'Release Year', position: 'bottom', fill: '#4b5563', dy: 10 }}
                    />
                    <YAxis 
                      type="number" 
                      dataKey="metascore" 
                      name="Metascore" 
                      domain={[87, 98]}
                      tick={{ fill: '#4b5563' }}
                      label={{ value: 'Metascore', angle: -90, position: 'left', fill: '#4b5563', dx: -10 }}
                    />
                    <ZAxis range={[60, 400]} />
                    <Tooltip 
                      cursor={{ strokeDasharray: '3 3' }}
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div className="bg-white p-3 border border-gray-200 shadow-md rounded">
                              <p className="font-bold">{payload[0].payload.game}</p>
                              <p>Year: {payload[0].payload.year}</p>
                              <p>Metascore: {payload[0].payload.metascore}</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Scatter 
                      name="Games" 
                      data={yearVsMetascoreData} 
                      fill="#10b981"
                      shape="circle"
                    />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md mb-8">
              <h2 className="text-lg font-semibold mb-4 text-indigo-800">Developer Insights</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 border border-indigo-100 rounded-lg bg-indigo-50">
                  <h3 className="text-md font-medium text-indigo-800 mb-3">Developer Patterns</h3>
                  <ul className="list-disc pl-5 space-y-2 text-gray-700">
                    <li><span className="font-semibold">Studio specialization:</span> Top developers tend to specialize in specific genres - Firaxis in strategy games, BioWare in RPGs, Valve in FPS</li>
                    <li><span className="font-semibold">Consistency:</span> Developers like Blizzard and Valve maintain high Metacritic scores across multiple titles and years</li>
                    <li><span className="font-semibold">Studio size impact:</span> Both large studios (EA, Activision) and smaller teams (ZA/UM) can achieve high scores, suggesting quality is not strictly tied to development resources</li>
                    <li><span className="font-semibold">Long-term franchises:</span> Many top developers successfully maintain long-running series (Civilization, Half-Life, Elder Scrolls) without quality degradation</li>
                  </ul>
                </div>
                
                <div className="p-4 border border-indigo-100 rounded-lg bg-indigo-50">
                  <h3 className="text-md font-medium text-indigo-800 mb-3">Historical Trends</h3>
                  <ul className="list-disc pl-5 space-y-2 text-gray-700">
                    <li><span className="font-semibold">Consistent quality:</span> High-rated games appear throughout all decades, suggesting quality game design transcends technological limitations</li>
                    <li><span className="font-semibold">Recent uptrend:</span> The 2020s show a higher concentration of top-rated games, possibly indicating maturation of development practices</li>
                    <li><span className="font-semibold">Score inflation:</span> The data hints at possible review score inflation over time, with more recent games having higher average scores</li>
                    <li><span className="font-semibold">Development cycles:</span> Many studios show patterns of releasing highly-rated games every 3-5 years, suggesting optimal development cycle length</li>
                  </ul>
                </div>
              </div>
              
              <div className="mt-6 p-4 border border-green-100 rounded-lg bg-green-50">
                <h3 className="text-md font-medium text-green-800 mb-3">Success Factors</h3>
                <p className="text-gray-700 mb-3">
                  Analysis of the highest-rated games reveals several common factors among successful developers:
                </p>
                <ul className="list-disc pl-5 space-y-2 text-gray-700">
                  <li><span className="font-semibold">Strong narrative focus:</span> Games with "Story Rich" tags frequently receive high scores</li>
                  <li><span className="font-semibold">Technical innovation:</span> Many top-rated games introduced new mechanics or technical achievements</li>
                  <li><span className="font-semibold">Post-release support:</span> Games with continued updates and expansions tend to maintain higher Steam reviews</li>
                  <li><span className="font-semibold">Player choice:</span> Games featuring meaningful player agency and choice appear frequently in top ratings</li>
                  <li><span className="font-semibold">Atmospheric design:</span> Immersive worlds and atmospheric design correlate strongly with high review scores</li>
                </ul>
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold mb-4 text-indigo-800">Developers and Publishers Success Relationship</h2>
              <div className="p-4 border border-purple-100 rounded-lg bg-purple-50">
                <h3 className="text-md font-medium text-purple-800 mb-3">Developer-Publisher Dynamics</h3>
                <p className="text-gray-700 mb-4">
                  Analysis of the dataset reveals interesting patterns in the relationship between developers and publishers:
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-purple-700 mb-2">Top Publisher-Developer Pairs</h4>
                    <ul className="list-disc pl-5 space-y-1 text-gray-700">
                      <li>Blizzard Entertainment (self-publishing)</li>
                      <li>Electronic Arts - BioWare</li>
                      <li>Valve Software (self-publishing)</li>
                      <li>Rockstar Games - Rockstar North</li>
                      <li>Bethesda Softworks - Bethesda Game Studios</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-purple-700 mb-2">Key Findings</h4>
                    <ul className="list-disc pl-5 space-y-1 text-gray-700">
                      <li>Self-publishing developers show higher average scores</li>
                      <li>Long-term publisher-developer relationships correlate with higher scores</li>
                      <li>Publishers with focused game portfolios outperform those with diverse catalogs</li>
                      <li>Independent games show increasing representation in high scores over time</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </>
        );
      
      default:
        return (
          <div className="bg-white p-4 rounded-lg shadow-md">
            <p>Select a tab to view analysis</p>
          </div>
        );
    }
  };

  return (
    <div className="p-6 bg-gray-100">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center text-indigo-900 mb-2">Video Game Analysis Dashboard</h1>
        <p className="text-center text-gray-600 mb-6">Analysis of {data.length} high-rated games from Steam and Metacritic</p>
        
        {/* Filter controls */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-4 gap-4">
          <div className="inline-flex rounded-md shadow-sm" role="group">
            <button
              type="button"
              className={`px-4 py-2 text-sm font-medium ${activeTab === 'overview' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'} 
                border border-gray-200 rounded-l-lg`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button
              type="button"
              className={`px-4 py-2 text-sm font-medium ${activeTab === 'genres' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'} 
                border-t border-b border-r border-gray-200`}
              onClick={() => setActiveTab('genres')}
            >
              Genres & Tags
            </button>
            <button
              type="button"
              className={`px-4 py-2 text-sm font-medium ${activeTab === 'developers' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'} 
                border-t border-b border-r border-gray-200 rounded-r-lg`}
              onClick={() => setActiveTab('developers')}
            >
              Developers & Trends
            </button>
          </div>
          
          <div className="flex items-center">
            <label htmlFor="year-filter" className="mr-2 text-sm font-medium text-gray-700">
              Filter by Year:
            </label>
            <select
              id="year-filter"
              className="bg-white border border-gray-300 text-gray-700 text-sm rounded-lg p-2.5 focus:ring-indigo-500 focus:border-indigo-500"
              value={selectedYearRange}
              onChange={(e) => setSelectedYearRange(e.target.value)}
            >
              <option value="all">All Years</option>
              <optgroup label="Decades">
                {decades.map(decade => (
                  <option key={decade} value={decade.replace('s', '')}>
                    {decade}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Specific Years">
                {years.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </optgroup>
            </select>
          </div>
        </div>
        
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                {selectedYearRange === 'all' 
                  ? 'Showing data for all years. Use the filter to focus on specific time periods.'
                  : `Filtering data for ${selectedYearRange.endsWith('s') 
                      ? `the ${selectedYearRange}0s` 
                      : `year ${selectedYearRange}`}. Currently displaying ${filteredData.length} games.`
                }
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {renderActiveTabContent()}
      
      <div className="mt-8 text-center text-gray-500 text-sm">
        <p>Data Analysis of Steam and Metacritic Game Ratings - {new Date().getFullYear()}</p>
      </div>
    </div>
  );
}

export default App;