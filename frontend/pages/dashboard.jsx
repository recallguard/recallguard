import { useEffect, useState } from 'react';
<<<<<<< HEAD
=======
import { SimpleGrid, Box, Text, Badge } from '@chakra-ui/react';
import { motion } from 'framer-motion';
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)

export default function Dashboard() {
  const [recalls, setRecalls] = useState(null);

  useEffect(() => {
    fetch('/api/recalls/recent')
      .then((res) => res.json())
      .then((data) => setRecalls(data))
      .catch(() => setRecalls([]));
  }, []);

  if (recalls === null) {
    return <div>Loading...</div>;
  }

  if (recalls.length === 0) {
    return (
<<<<<<< HEAD
      <div style={{ color: 'green' }}>
        No recent recalls.
      </div>
=======
      <div className="text-green-600">No recent recalls.</div>
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
    );
  }

  const truncate = (text) =>
    text && text.length > 50 ? text.slice(0, 50) + '…' : text;

<<<<<<< HEAD
  const badgeColor = (source) => {
    const colors = {
      cpsc: '#FFB703',
      fda: '#8ECAE6',
      nhtsa: '#90BE6D',
      usda: '#FB8500'
    };
    return { backgroundColor: colors[source.toLowerCase()] || '#ddd', padding: '2px 6px', borderRadius: '4px', color: '#000' };
  };

  return (
    <table>
      <thead>
        <tr>
          <th>Product</th>
          <th>Hazard</th>
          <th>Date</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
        {recalls.map((r) => (
          <tr key={`${r.source}-${r.id}`}>
            <td>{r.product}</td>
            <td>{truncate(r.hazard)}</td>
            <td>{r.recall_date}</td>
            <td>
              <span style={badgeColor(r.source)}>{r.source}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
=======
  const hazardColor = (hazard) => {
    const h = (hazard || '').toLowerCase();
    if (h.includes('fire')) return 'red';
    if (h.includes('injury')) return 'orange';
    if (h.includes('chemical')) return 'yellow';
    return 'gray';
  };

  const MotionBox = motion(Box);

  return (
    <SimpleGrid columns={{ base: 1, sm: 2, md: 3, lg: 4 }} spacing={4} p={4}>
      {recalls.map((r) => (
        <MotionBox
          key={`${r.source}-${r.id}`}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
        >
          <Text fontWeight="bold" noOfLines={2} mb={2}>
            {r.product}
          </Text>
          <Badge colorScheme={hazardColor(r.hazard)} mr={2} aria-label="hazard">
            {truncate(r.hazard)}
          </Badge>
          <Badge>{r.source.toUpperCase()}</Badge>
          <Text mt={2} fontSize="sm">
            {r.recall_date}
          </Text>
        </MotionBox>
      ))}
    </SimpleGrid>
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
  );
}

