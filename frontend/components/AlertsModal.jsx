import { useDisclosure, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton, Button, Input, HStack, VStack, Switch, FormControl, FormLabel } from '@chakra-ui/react';
import { useState, useContext } from 'react';
import { AuthContext } from './AuthContext.jsx';
import { useSubscriptions } from '../hooks/useSubscriptions.js';

export default function AlertsModal() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { token } = useContext(AuthContext);
  const { subs, remove } = useSubscriptions();
  const [query, setQuery] = useState('');
  const [source, setSource] = useState('cpsc');
  const [enabled, setEnabled] = useState(false);

  const saveSub = async () => {
    await fetch('/api/subscriptions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ recall_source: source, product_query: query }),
    });
    setQuery('');
  };

  const toggleEmail = async () => {
    await fetch('/api/email-opt-in', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ enabled: !enabled }),
    });
    setEnabled(!enabled);
  };

  return (
    <>
      <Button onClick={onOpen}>⚡ Alerts</Button>
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Alert Subscriptions</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl display="flex" alignItems="center" mb={4}>
              <FormLabel htmlFor="email-enabled" mb="0">
                Email alerts
              </FormLabel>
              <Switch id="email-enabled" isChecked={enabled} onChange={toggleEmail} />
            </FormControl>
            <VStack align="stretch" spacing={2} mb={4}>
              {subs.map((s) => (
                <HStack key={s.id} justify="space-between">
                  <span>
                    {s.recall_source.toUpperCase()} – {s.product_query}
                  </span>
                  <Button size="xs" onClick={() => remove(s.id)}>
                    Delete
                  </Button>
                </HStack>
              ))}
            </VStack>
            <HStack>
              <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="product" />
              <Button size="sm" onClick={saveSub} isDisabled={!query}>
                Add
              </Button>
            </HStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
}
