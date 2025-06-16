import { useEffect, useState } from 'react';
import { SimpleGrid, Box, Text, Badge } from '@chakra-ui/react';
import { motion } from 'framer-motion';

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
      <div className="text-green-600">No recent recalls.</div>
    );
  }

  const truncate = (text) =>
    text && text.length > 50 ? text.slice(0, 50) + '…' : text;

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
  );
}

