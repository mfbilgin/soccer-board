import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Modal, TextInput, TouchableOpacity, FlatList, ActivityIndicator, Image } from 'react-native';
import { COLORS, SIZES, GLOBAL_STYLES } from '../theme';
import api from '../api';

export default function SearchModal({ visible, onClose, onSelect, searchType }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (visible) {
      setQuery('');
      setResults([]);
      setLoading(false);
    }
  }, [visible]);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (query.length >= 2) {
        performSearch();
      } else {
        setResults([]);
        setLoading(false);
      }
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  const performSearch = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/game/tictactoe/search?q=${query}&type=${searchType}`);
      setResults(res.data.results);
    } catch (err) {
      console.log(err);
    } finally {
      setLoading(false);
    }
  };

  const placeholderText = searchType === 1 ? "Bir futbolcu ara (Örn: Messi)" : "Bir takım ara (Örn: Real Madrid)";

  return (
    <Modal visible={visible} animationType="slide" transparent={true}>
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          
          <View style={styles.header}>
            <Text style={GLOBAL_STYLES.textTitle}>Tahmin Et</Text>
            <TouchableOpacity onPress={onClose}>
              <Text style={{color: COLORS.danger, fontSize: 18}}>Kapat</Text>
            </TouchableOpacity>
          </View>

          <TextInput
            style={styles.searchInput}
            placeholder={placeholderText}
            placeholderTextColor={COLORS.textMuted}
            value={query}
            onChangeText={setQuery}
            autoFocus
          />

          {loading ? (
            <ActivityIndicator style={{marginTop: 20}} color={COLORS.primary} />
          ) : (
            <FlatList
              data={results}
              keyExtractor={(item) => item.id.toString()}
              contentContainerStyle={{ paddingBottom: 20 }}
              renderItem={({ item }) => (
                <TouchableOpacity 
                  style={styles.resultItem}
                  onPress={() => onSelect(item)}
                >
                  <View style={{flexDirection: 'column'}}>
                    <Text style={styles.resultText}>{item.name}</Text>
                    {item.subtitle ? <Text style={{color: 'gray', fontSize: 12, marginTop: 2}}>{item.subtitle}</Text> : null}
                  </View>
                </TouchableOpacity>
              )}
            />
          )}

        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: COLORS.background,
    height: '80%',
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    padding: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  searchInput: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    color: COLORS.text,
    height: 50,
    borderRadius: SIZES.radius,
    paddingHorizontal: 15,
    fontSize: SIZES.medium,
    borderWidth: 1,
    borderColor: COLORS.primary,
    marginBottom: 15,
  },
  resultItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderBottomWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  resultImage: {
    width: 40,
    height: 40,
    borderRadius: 20,
    marginRight: 15,
  },
  resultImagePlaceholder: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginRight: 15,
  },
  resultText: {
    color: COLORS.text,
    fontSize: SIZES.medium,
  }
});
