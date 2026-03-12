import React, { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  DoughnutController,
  ArcElement
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  DoughnutController,
  ArcElement
);

interface ChartProps {
  type: 'line' | 'bar' | 'doughnut' | 'pie';
  data: any[];
  height?: number;
  options?: any;
}

const AnalyticsChart: React.FC<ChartProps> = ({ type, data, height = 250, options = {} }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<ChartJS | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Destroy previous chart
    if (chartRef.current) {
      chartRef.current.destroy();
    }

    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    // Prepare data based on chart type
    let chartData: any = {};

    if (type === 'line') {
      chartData = {
        labels: data.map(d => d.label),
        datasets: [{
          label: 'Views',
          data: data.map(d => d.value),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true
        }]
      };
    } else if (type === 'doughnut' || type === 'pie') {
      const colors = [
        'rgb(59, 130, 246)',
        'rgb(14, 165, 233)',
        'rgb(99, 102, 241)',
        'rgb(139, 92, 246)',
        'rgb(168, 85, 247)',
        'rgb(192, 132, 252)',
        'rgb(232, 121, 249)',
        'rgb(244, 114, 182)'
      ];

      chartData = {
        labels: data.map(d => d.referrer || d.country),
        datasets: [{
          data: data.map(d => d.visits || d.visitors || d.value),
          backgroundColor: colors.slice(0, data.length),
          borderColor: 'rgba(255, 255, 255, 1)',
          borderWidth: 2
        }]
      };
    } else if (type === 'bar') {
      chartData = {
        labels: data.map(d => d.label),
        datasets: [{
          label: 'Count',
          data: data.map(d => d.value),
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 1
        }]
      };
    }

    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: type === 'line' ? 'top' : 'right',
          labels: {
            usePointStyle: true,
            boxWidth: 6,
            font: {
              size: 12
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          cornerRadius: 6,
          titleFont: {
            size: 14,
            weight: 'bold'
          },
          bodyFont: {
            size: 13
          }
        }
      }
    };

    if (type === 'line') {
      defaultOptions.scales = {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            font: {
              size: 11
            }
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: {
              size: 11
            }
          }
        }
      };
    }

    chartRef.current = new ChartJS(ctx, {
      type: type === 'doughnut' ? 'doughnut' : type,
      data: chartData,
      options: { ...defaultOptions, ...options }
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [type, data, options]);

  return (
    <div style={{ height: `${height}px` }}>
      <canvas ref={canvasRef}></canvas>
    </div>
  );
};

export default AnalyticsChart;