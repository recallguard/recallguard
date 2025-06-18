import { useEffect, useState } from 'react';
import { SimpleGrid, Box, Text, Badge } from '@chakra-ui/react';

export default function Dashboard() {
  const [recalls, setRecalls] = useState([]);

  useEffect(() => {
    fetch('/api/recalls/recent')
      .then((r) => r.json())
      .then((data) => setRecalls(data))
      .catch(() => setRecalls([]));
  }, []);

  const hazardColor = (hazard) => {
    const h = (hazard || '').toLowerCase();
    if (h.includes('fire')) return 'red';
    if (h.includes('injury')) return 'orange';
    if (h.includes('chemical')) return 'yellow';
    return 'gray';
  };

  if (recalls.length === 0) {
    return <div>No recent recalls.</div>;
  }

  return (
    <SimpleGrid columns={{ base: 1, sm: 2, md: 3, lg: 4 }} spacing={4} p={4}>
      {recalls.map((r) => (
        <Box key={`${r.source}-${r.id}`} p={4} borderWidth="1px" borderRadius="md">
          <Text fontWeight="bold" noOfLines={2} mb={2}>
            {r.product}
          </Text>
          <Badge colorScheme={hazardColor(r.hazard)} mr={2} aria-label="hazard">
            {r.hazard}
          </Badge>
          <Badge>{r.source.toUpperCase()}</Badge>
          {r.summary_text && (
            <Text mt={2} fontSize="sm">{r.summary_text}</Text>
          )}
          {r.next_steps && (
            <Text mt={2} fontSize="sm" color="green.700">{r.next_steps}</Text>
          )}
          <Text mt={2} fontSize="sm">
            {r.recall_date}
          </Text>
        </Box>
      ))}
    </SimpleGrid>
  );
}
