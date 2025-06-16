import { useEffect, useMemo, useRef, useState } from 'react';
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Box,
  Input,
  Drawer,
  DrawerOverlay,
  DrawerContent,
  DrawerHeader,
  DrawerBody,
  useDisclosure,
  Skeleton,
  Center,
  Link as ChakraLink,
  Text,
} from '@chakra-ui/react';
import { useReactTable, getCoreRowModel, getFilteredRowModel } from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import ReactMarkdown from 'react-markdown';

export default function Dashboard() {
  const [recalls, setRecalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [selected, setSelected] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const parentRef = useRef();

  useEffect(() => {
    fetch('/api/recalls/recent?limit=5000')
      .then((res) => res.json())
      .then((data) => {
        setRecalls(data);
        setLoading(false);
      })
      .catch(() => {
        setRecalls([]);
        setLoading(false);
      });
  }, []);

  const columns = useMemo(
    () => [
      { accessorKey: 'product', header: 'Product' },
      { accessorKey: 'hazard', header: 'Hazard' },
      { accessorKey: 'recall_date', header: 'Date' },
      {
        accessorKey: 'source',
        header: 'Source',
        cell: (info) => <Badge>{info.getValue().toUpperCase()}</Badge>,
      },
    ],
    []
  );

  const table = useReactTable({
    data: recalls,
    columns,
    state: { globalFilter: filter },
    getFilteredRowModel: getFilteredRowModel(),
    getCoreRowModel: getCoreRowModel(),
  });

  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35,
    overscan: 10,
  });

  const openDrawer = (row) => {
    setSelected(row.original);
    onOpen();
  };

  const rows = rowVirtualizer.getVirtualItems();

  return (
    <Box p={4}>
      <Input
        placeholder="Search recalls..."
        mb={4}
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        aria-label="Search"
      />
      <Box ref={parentRef} height="60vh" overflowY="auto">
        <Table size="sm" variant="striped">
          <Thead position="sticky" top={0} bg="chakra-body-bg" zIndex={1}>
            {table.getHeaderGroups().map((headerGroup) => (
              <Tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <Th key={header.id}>{header.column.columnDef.header}</Th>
                ))}
              </Tr>
            ))}
          </Thead>
          <Tbody>
            {loading
              ? [...Array(5)].map((_, i) => (
                  <Tr key={i}>
                    <Td colSpan={4}>
                      <Skeleton height="20px" />
                    </Td>
                  </Tr>
                ))
              : rows.map((virtualRow) => {
                  const row = table.getRowModel().rows[virtualRow.index];
                  return (
                    <Tr
                      key={row.id}
                      role="button"
                      tabIndex={0}
                      onClick={() => openDrawer(row)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') openDrawer(row);
                      }}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <Td key={cell.id}>
                          {cell.column.columnDef.cell
                            ? cell.column.columnDef.cell(cell)
                            : cell.getValue()}
                        </Td>
                      ))}
                    </Tr>
                  );
                })}
          </Tbody>
        </Table>
        {!loading && table.getRowModel().rows.length === 0 && (
          <Center py={10}>No recent recalls.</Center>
        )}
      </Box>

      <Drawer isOpen={isOpen} onClose={onClose} size={{ base: 'full', md: 'md' }}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerHeader fontSize="lg" fontWeight="bold">
            {selected?.product}
          </DrawerHeader>
          <DrawerBody>
            {selected && (
              <Box className="prose">
                <Badge mb={2}>{selected.hazard}</Badge>
                <Text mb={2}>{selected.recall_date}</Text>
                <ReactMarkdown>{selected.description}</ReactMarkdown>
                {selected.url && (
                  <ChakraLink href={selected.url} color="blue.500" isExternal>
                    Official Notice
                  </ChakraLink>
                )}
              </Box>
            )}
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Box>
  );
}
