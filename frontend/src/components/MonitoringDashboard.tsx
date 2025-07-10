import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Treemap, ScatterChart, Scatter, ZAxis
} from 'recharts';
import { Card, Grid, Typography, Box, CircularProgress, Tabs, Tab } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import {
  DashboardData,
  ProcessingData,
  HeatmapItem,
  TreemapItem,
  TooltipProps,
  TreemapContentProps
} from './types';

interface DashboardProps {
  refreshInterval?: number;  // in milliseconds
}

interface ChartData {
  name: string;
  avgDuration: number;
  avgMemory: number;
  avgCpu: number;
  count: number;
  maxDuration: number;
}

const MonitoringDashboard: React.FC<DashboardProps> = ({ refreshInterval = 60000 }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [performanceData, setPerformanceData] = useState<DashboardData | null>(null);
  const [processingData, setProcessingData] = useState<ProcessingData | null>(null);
  
  const COLORS = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.error.main,
    theme.palette.warning.main,
    theme.palette.success.main,
  ];
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [perfResponse, procResponse] = await Promise.all([
          fetch('/api/dashboard/performance'),
          fetch('/api/dashboard/processing')
        ]);
        
        const perfData = await perfResponse.json();
        const procData = await procResponse.json();
        
        setPerformanceData(perfData);
        setProcessingData(procData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);
  
  const renderPerformanceMetrics = () => {
    if (!performanceData?.performance) return null;
    
    const data = Object.entries(performanceData.performance).map(([name, metrics]: [string, any]) => ({
      name,
      avgDuration: metrics.avg_duration,
      avgMemory: metrics.avg_memory,
      avgCpu: metrics.avg_cpu,
      count: metrics.count,
      maxDuration: metrics.max_duration
    }));
    
    // Prepare heatmap data
    const heatmapData = data.map(item => ({
      name: item.name,
      x: item.avgMemory,
      y: item.avgCpu,
      z: item.avgDuration,
      value: item.count
    }));
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <Typography variant="h6" p={2}>Performance Radar</Typography>
            <Box height={300}>
              <ResponsiveContainer>
                <RadarChart data={data}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="name" />
                  <PolarRadiusAxis />
                  <Radar
                    name="Duration"
                    dataKey="avgDuration"
                    stroke={COLORS[0]}
                    fill={COLORS[0]}
                    fillOpacity={0.6}
                  />
                  <Radar
                    name="Memory"
                    dataKey="avgMemory"
                    stroke={COLORS[1]}
                    fill={COLORS[1]}
                    fillOpacity={0.6}
                  />
                  <Tooltip />
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </Box>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <Typography variant="h6" p={2}>Resource Usage Heatmap</Typography>
            <Box height={300}>
              <ResponsiveContainer>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="x"
                    name="Memory Usage (MB)"
                    type="number"
                  />
                  <YAxis
                    dataKey="y"
                    name="CPU Usage (%)"
                    type="number"
                  />
                  <ZAxis
                    dataKey="z"
                    range={[50, 1000]}
                    name="Duration"
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    content={({ payload }: TooltipProps) => {
                      if (payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div style={{ backgroundColor: 'white', padding: '10px', border: '1px solid #ccc' }}>
                            <p>{`Operation: ${data.name}`}</p>
                            <p>{`Memory: ${data.x.toFixed(2)} MB`}</p>
                            <p>{`CPU: ${data.y.toFixed(2)}%`}</p>
                            <p>{`Duration: ${data.z.toFixed(2)}s`}</p>
                            <p>{`Count: ${data.value}`}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Scatter
                    data={heatmapData}
                    fill={COLORS[0]}
                    fillOpacity={0.6}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </Box>
          </Card>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <Typography variant="h6" p={2}>Operation Performance Treemap</Typography>
            <Box height={300}>
              <ResponsiveContainer>
                <Treemap
                  data={data.map(item => ({
                    name: item.name,
                    size: item.count,
                    duration: item.avgDuration,
                    memory: item.avgMemory,
                    cpu: item.avgCpu
                  }))}
                  dataKey="size"
                  stroke="#fff"
                  fill={COLORS[0]}
                  content={({ root, depth, x, y, width, height, index, payload, colors, rank, name }: TreemapContentProps) => {
                    return (
                      <g>
                        <rect
                          x={x}
                          y={y}
                          width={width}
                          height={height}
                          style={{
                            fill: COLORS[index % COLORS.length],
                            stroke: '#fff',
                            strokeWidth: 2 / (depth + 1e-10),
                            strokeOpacity: 1 / (depth + 1e-10),
                          }}
                        />
                        {width > 50 && height > 30 && (
                          <text
                            x={x + width / 2}
                            y={y + height / 2}
                            textAnchor="middle"
                            fill="#fff"
                            fontSize={14}
                          >
                            {name}
                          </text>
                        )}
                      </g>
                    );
                  }}
                />
              </ResponsiveContainer>
            </Box>
          </Card>
        </Grid>
      </Grid>
    );
  };
  
  const renderProcessingMetrics = () => {
    if (!processingData?.processing_stats) return null;
    
    const { documents, blocks } = processingData.processing_stats;
    const blockTypes = Object.entries(blocks.by_type).map(([type, count]) => ({
      name: type,
      value: count
    }));
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <Typography variant="h6" p={2}>Document Processing</Typography>
            <Box height={300}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Processed', value: documents.processed },
                      { name: 'Pending', value: documents.total - documents.processed }
                    ]}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    fill="#8884d8"
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {blockTypes.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <Typography variant="h6" p={2}>Block Types Distribution</Typography>
            <Box height={300}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={blockTypes}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {blockTypes.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Card>
        </Grid>
      </Grid>
    );
  };
  
  const renderNLPMetrics = () => {
    if (!processingData?.nlp_metrics) return null;
    
    const { entity_types, complexity_scores } = processingData.nlp_metrics;
    const entityData = Object.entries(entity_types).map(([type, count]) => ({
      name: type,
      value: count
    }));
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <Typography variant="h6" p={2}>Entity Type Distribution</Typography>
            <Box height={300}>
              <ResponsiveContainer>
                <BarChart data={entityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill={COLORS[0]} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <Typography variant="h6" p={2}>Text Complexity Distribution</Typography>
            <Box height={300}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={Object.entries(complexity_scores).map(([level, count]) => ({
                      name: level,
                      value: count
                    }))}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {Object.keys(complexity_scores).map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Card>
        </Grid>
      </Grid>
    );
  };
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        System Monitoring Dashboard
      </Typography>
      
      <Tabs
        value={activeTab}
        onChange={(_: React.SyntheticEvent, newValue: number) => setActiveTab(newValue)}
        sx={{ mb: 3 }}
      >
        <Tab label="Performance" />
        <Tab label="Processing" />
        <Tab label="NLP Metrics" />
      </Tabs>
      
      {activeTab === 0 && renderPerformanceMetrics()}
      {activeTab === 1 && renderProcessingMetrics()}
      {activeTab === 2 && renderNLPMetrics()}
    </Box>
  );
};

export default MonitoringDashboard;
