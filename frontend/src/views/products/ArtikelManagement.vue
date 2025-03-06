<template>
    <div class="artikel-management">
        <!-- Header -->
        <div class="artikel-header">
            <div class="artikel-title"><span class="artikel-heart">❤</span><span>Artikel</span>
            </div>
            <div class="window-controls">
                <button class="window-control-button" @click="minimizeWindow"><span>_</span>
                </button>
                <button class="window-control-button" @click="maximizeWindow"><span>□</span>
                </button>
                <button class="window-control-button" @click="closeWindow"><span>×</span>
                </button>
            </div>
        </div>
        <!-- Toolbar -->
        <div class="artikel-toolbar">
            <button class="toolbar-button">
                <PlusIcon class="icon-small"/>
            </button>
            <button class="toolbar-button">
                <MinusIcon class="icon-small"/>
            </button>
            <div class="search-input-container">
                <AtSignIcon class="search-icon"/>
                <input class="search-input" placeholder="Search..."/>
            </div>
            <button class="toolbar-button">
                <TypeIcon class="icon-small"/>
            </button>
            <button class="toolbar-button">
                <EyeIcon class="icon-small"/>
            </button>
            <button class="toolbar-button">
                <SearchIcon class="icon-small"/>
            </button>
            <button class="toolbar-button">
                <FileTextIcon class="icon-small"/>
            </button>
            <button class="artikel-button">
                Artikel übernehmen
            </button>
            <div class="toolbar-right">
                <button class="toolbar-button">
                    <RotateCcwIcon class="icon-small"/>
                </button>
                <button class="toolbar-button">
                    <SettingsIcon class="icon-small"/>
                </button>
            </div>
        </div>
        <!-- Main Content -->
        <div class="artikel-content">
            <!-- Left Panel - Product List -->
            <div class="product-list-panel">
                <div class="list-header">
                    <div class="nummer-column">Nummer</div>
                    <div class="bezeichnung-column">Bezeichnung</div>
                </div>
                <div class="product-list-container">
                    <div v-for="product in productData" 
                         :key="product.nummer" 
                         :class="['product-list-item', product.selected ? 'selected' : '']" 
                         @click="selectProduct(product)">
                        <div class="nummer-column">{{ product.nummer }}</div>
                        <div class="bezeichnung-column">{{ product.bezeichnung }}</div>
                    </div>
                </div>
            </div>
            <!-- Right Panel - Product Details -->
            <div class="product-details-panel">
                <div class="details-container">
                    <!-- Tabs -->
                    <div class="tabs-container">
                        <button :class="['tab-button', activeTab === 'mutter' ? 'active' : '']" 
                                @click="activeTab = 'mutter'">
                            Mutter
                        </button>
                        <button :class="['tab-button', activeTab === 'varianten' ? 'active' : '']" 
                                @click="activeTab = 'varianten'">
                            Varianten
                        </button>
                    </div>
                    <!-- Tab Content -->
                    <div v-if="activeTab === 'mutter'" class="tab-content">
                        <div class="form-sections">
                            <!-- Bezeichnung -->
                            <div class="form-section">
                                <div class="section-header">
                                    <label class="section-label">Bezeichnung</label>
                                    <div class="section-actions">
                                        <button class="action-button">
                                            <PlusIcon class="icon-tiny"/>
                                        </button>
                                        <button class="action-button">
                                            <MinusIcon class="icon-tiny"/>
                                        </button>
                                    </div>
                                </div>
                                <div class="input-with-button">
                                    <input class="form-input" v-model="selectedProductData.bezeichnung"/>
                                    <button class="form-button">
                                        <FlagIcon class="icon-small"/>
                                    </button>
                                </div>
                            </div>
                            <!-- Beschreibung -->
                            <div class="form-section">
                                <label class="section-label">Beschreibung</label>
                                <textarea class="form-textarea" v-model="selectedProductData.beschreibung"></textarea>
                            </div>
                            <!-- Maße -->
                            <div class="form-section">
                                <div class="section-header">
                                    <label class="section-label">Maße</label>
                                    <div class="section-actions">
                                        <span class="section-label-small">Tags</span>
                                        <button class="action-button">
                                            <MinusIcon class="icon-tiny"/>
                                        </button>
                                    </div>
                                </div>
                                <div class="two-column-grid">
                                    <div class="form-column">
                                        <div class="checkbox-field">
                                            <input type="checkbox" id="hangend" v-model="selectedProductData.hangend" class="form-checkbox"/>
                                            <label for="hangend" class="checkbox-label">Hängend</label>
                                        </div>
                                        <div class="checkbox-field">
                                            <input type="checkbox" id="einseitig" v-model="selectedProductData.einseitig" class="form-checkbox"/>
                                            <label for="einseitig" class="checkbox-label">Einseitig</label>
                                        </div>
                                        <div class="labeled-input">
                                            <label class="input-label">Breite</label>
                                            <input class="small-input" v-model="selectedProductData.breite"/>
                                        </div>
                                        <div class="labeled-input">
                                            <label class="input-label">Höhe</label>
                                            <input class="small-input" v-model="selectedProductData.hohe"/>
                                        </div>
                                        <div class="labeled-input">
                                            <label class="input-label">Tiefe</label>
                                            <input class="small-input" v-model="selectedProductData.tiefe"/>
                                        </div>
                                        <div class="labeled-input">
                                            <label class="input-label">Gewicht</label>
                                            <input class="small-input" v-model="selectedProductData.gewicht"/>
                                        </div>
                                    </div>
                                    <div class="form-column">
                                        <div class="labeled-input">
                                            <label class="input-label">Boxgröße</label>
                                            <input class="medium-input" v-model="selectedProductData.boxgrosse"/>
                                        </div>
                                        <div class="form-field">
                                            <label class="section-label">Tags</label>
                                            <input class="form-input" v-model="selectedProductData.tags"/>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <!-- Kategorien -->
                            <div class="form-section">
                                <div class="section-header">
                                    <label class="section-label">Kategorien</label>
                                    <div class="section-actions">
                                        <button class="action-button">
                                            <PlusIcon class="icon-tiny"/>
                                        </button>
                                        <button class="action-button">
                                            <MinusIcon class="icon-tiny"/>
                                        </button>
                                    </div>
                                </div>
                                <div class="table-container">
                                    <table class="data-table">
                                        <thead>
                                            <tr>
                                                <th v-for="(header, i) in categoriesHeaders" :key="i" class="table-header">
                                                    {{ header }}
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="(row, rowIndex) in categoriesData" :key="rowIndex">
                                                <td v-for="(cell, cellIndex) in row" :key="cellIndex" class="table-cell">
                                                    {{ cell }}
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-if="activeTab === 'varianten'" class="tab-content">
                        <p class="empty-message">Varianten-Inhalte würden hier angezeigt werden.</p>
                    </div>
                </div>
                <!-- Right Side Panel -->
                <div class="side-panel">
                    <div class="side-panel-header">
                        <span class="section-label">Besteht aus</span>
                        <span class="section-label">Anz</span>
                    </div>
                    <div class="table-container">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th class="table-header">DE</th>
                                    <th class="table-header"></th>
                                    <th class="table-header"></th>
                                    <th class="table-header"></th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="table-cell">EN</td>
                                    <td class="table-cell"></td>
                                    <td class="table-cell"></td>
                                    <td class="table-cell"></td>
                                </tr>
                                <tr v-for="i in 10" :key="i">
                                    <td class="table-cell"></td>
                                    <td class="table-cell"></td>
                                    <td class="table-cell"></td>
                                    <td class="table-cell"></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="publish-button-container">
                        <button class="publish-button">
                            Publish
                        </button>
                    </div>
                    <div class="help-button-container">
                        <div class="help-button">
                            ?
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, watch, defineProps, defineEmits } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { 
  Plus as PlusIcon, 
  Minus as MinusIcon, 
  AtSign as AtSignIcon, 
  Type as TypeIcon, 
  Eye as EyeIcon, 
  Search as SearchIcon, 
  FileText as FileTextIcon, 
  RotateCcw as RotateCcwIcon, 
  Settings as SettingsIcon,
  Flag as FlagIcon,
  X as XIcon
} from 'lucide-vue-next';
import { productApi } from '@/services/api';

// Define props and emits
const props = defineProps({
  product: {
    type: Object,
    default: null
  },
  id: {
    type: [String, Number],
    default: null
  }
});

const emit = defineEmits(['close']);
const route = useRoute();
const router = useRouter();

// State for loading product data
const isLoadingProduct = ref(false);
const productLoadError = ref('');

// Sample data for the product list
const productData = ref([
  { nummer: "307967", bezeichnung: "" },
  { nummer: "132355", bezeichnung: "" },
  { nummer: "-1", bezeichnung: "" },
  { nummer: "912859", bezeichnung: "\"Adler\"-Erste Eisenbahn" },
  { nummer: "218300", bezeichnung: "\"Adler\"-Lock" },
  { nummer: "310048", bezeichnung: "\"Adler\"-Tender" },
  { nummer: "411430", bezeichnung: "\"Adler\"-Wagen" },
  { nummer: "409129", bezeichnung: "\"Adler\"-Wagen-offen", selected: true },
  { nummer: "300251", bezeichnung: "\"Adler\"-Wagen/Führer" },
  { nummer: "922678", bezeichnung: "100-0" },
  { nummer: "325473", bezeichnung: "100-0/3" },
  { nummer: "530620", bezeichnung: "100-0/5" },
  { nummer: "921063", bezeichnung: "1x Saugnapf für Glasscheibe Vitrine" },
  { nummer: "903786", bezeichnung: "22 Zoll Display Sichtschutz Bildschirm" },
  { nummer: "718205", bezeichnung: "27 Zoll Display Sichtschutz Bildschirm" },
  { nummer: "701703", bezeichnung: "5x BelegDrucker Rollen" },
  { nummer: "831738", bezeichnung: "7 miniatur Hasen in drei Teile" },
  { nummer: "309069", bezeichnung: "7 Schwaben mit Hase" },
  { nummer: "811140", bezeichnung: "80-2" },
  { nummer: "304527", bezeichnung: "80-4" },
  { nummer: "219557", bezeichnung: "Abschiles Planen Draht Seil Nürnberg" },
  { nummer: "218118", bezeichnung: "ADAC Bus" },
  { nummer: "717971", bezeichnung: "Adam und Eva" },
  { nummer: "729258", bezeichnung: "Adler Lock(Weygang 1830)" },
  { nummer: "224917", bezeichnung: "Adler Zug klein" },
  { nummer: "414760", bezeichnung: "Adventskranz" },
  { nummer: "326122", bezeichnung: "Adventskranz 3D" },
  { nummer: "523275", bezeichnung: "Adventskranz mit Puten" },
  { nummer: "525070", bezeichnung: "Aeffchen" },
  { nummer: "701792", bezeichnung: "Akkupack Batterie Powerbank" },
  { nummer: "717761", bezeichnung: "Alchimist" },
  { nummer: "705870", bezeichnung: "Alchimist klein" },
  { nummer: "105515", bezeichnung: "alter Raddampfer Diessen" },
]);

// Selected product data
const selectedProductData = reactive({
  bezeichnung: '"Adler"-Wagen-offen',
  beschreibung: 'Tauchen Sie ein in eine Ära eleganter Fahrten und vornehmer Gesellschaften mit dieser exquisiten Zinnfigur. Ein nostalgischer Wagen, kunstvoll gestaltet, bietet Sitz für sechs Personen in festlicher Garderobe, welche die feine Eleganz vergangener Tage widerspiegeln. Ideal als Geschenk oder für die eigene Sammlung, misst dieses Meisterwerk 6.0 x 5.0 cm und verkörpert die Schönheit und den Geist traditioneller Handwerkskunst. Ein Schmuckstück, das jede Vitrine bereichert.',
  hangend: false,
  einseitig: false,
  breite: '5',
  hohe: '6',
  tiefe: '0,7',
  gewicht: '20',
  boxgrosse: 'B2',
  tags: ''
});

// Active tab
const activeTab = ref('mutter');

// Categories data
const categoriesHeaders = ['Home', 'Sortiment', 'Tradition', 'Maschinerie'];
const categoriesData = [
  ['', '', 'Home', 'All Products']
];

// Select product function
const selectProduct = (product: { nummer: string; bezeichnung: string; selected?: boolean }) => {
  productData.value.forEach(p => p.selected = false);
  product.selected = true;
};

// Window control functions
const minimizeWindow = () => {
  console.log('Minimize window');
};

const maximizeWindow = () => {
  console.log('Maximize window');
};

const closeWindow = () => {
  // If we're in a modal, emit close event
  if (props.product) {
    emit('close');
  } 
  // If we're in a standalone page, navigate back
  else {
    router.back();
  }
};

// Load product data from API
const loadProductFromApi = async (productId: string | number) => {
  isLoadingProduct.value = true;
  productLoadError.value = '';
  
  try {
    console.log('Loading product data for ID:', productId);
    // Ensure productId is a number
    const id = typeof productId === 'string' ? parseInt(productId, 10) : productId;
    const response = await productApi.getProduct(id);
    
    if (response && response.data) {
      console.log('Product data loaded:', response.data);
      
      // Map API product data to ArtikelManagement format
      if (response.data.name) {
        selectedProductData.bezeichnung = response.data.name;
      }
      
      if (response.data.description) {
        selectedProductData.beschreibung = response.data.description;
      }
      
      // Select the corresponding product in the list if it exists
      if (response.data.sku) {
        const matchingProduct = productData.value.find(p => p.nummer === response.data.sku);
        if (matchingProduct) {
          selectProduct(matchingProduct);
        }
      }
    }
  } catch (err: any) {
    console.error('Error loading product:', err);
    productLoadError.value = `Failed to load product: ${err.message || 'Unknown error'}`;
  } finally {
    isLoadingProduct.value = false;
  }
};

// Watch for product prop changes
watch(() => props.product, (newProduct) => {
  if (newProduct) {
    console.log('Product data received via prop:', newProduct);
    // Map the product data to the ArtikelManagement format if needed
    
    // For example:
    if (newProduct.name) {
      selectedProductData.bezeichnung = newProduct.name;
    }
    
    if (newProduct.description) {
      selectedProductData.beschreibung = newProduct.description;
    }
    
    // Select the corresponding product in the list if it exists
    if (newProduct.sku) {
      const matchingProduct = productData.value.find(p => p.nummer === newProduct.sku);
      if (matchingProduct) {
        selectProduct(matchingProduct);
      }
    }
  }
}, { immediate: true });

// Watch for route param changes
watch(() => route.params.id, (newId) => {
  if (newId && !props.product) {
    // Ensure newId is a string or number, not an array
    const id = Array.isArray(newId) ? newId[0] : newId;
    loadProductFromApi(id);
  }
}, { immediate: true });

onMounted(() => {
  console.log('ArtikelManagement component mounted');
  console.log('Initial product prop:', props.product);
  console.log('Route params:', route.params);
  
  // If we have an ID from the route and no product prop, load the product
  const routeId = route.params.id || props.id;
  if (routeId && !props.product) {
    // Ensure routeId is a string or number, not an array
    const id = Array.isArray(routeId) ? routeId[0] : routeId;
    loadProductFromApi(id);
  }
});
</script>
<style scoped>
.artikel-management {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Header styles */
.artikel-header {
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
  padding: 10px;
  border-bottom: 1px solid #ddd;
}

.artikel-title {
  display: flex;
  align-items: center;
  font-weight: 600;
}

.artikel-heart {
  color: #d2bc9b;
  font-weight: bold;
  margin-right: 5px;
}

.window-controls {
  margin-left: auto;
  display: flex;
  gap: 5px;
}

.window-control-button {
  padding: 4px 8px;
  background-color: #eaeaea;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.window-control-button:hover {
  background-color: #d5d5d5;
}

/* Toolbar styles */
.artikel-toolbar {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #ddd;
}

.toolbar-button {
  height: 32px;
  width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  margin-right: 5px;
  cursor: pointer;
}

.toolbar-button:hover {
  background-color: #f0f0f0;
}

.search-input-container {
  position: relative;
  margin-right: 5px;
}

.search-icon {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  height: 16px;
  width: 16px;
}

.search-input {
  height: 32px;
  padding-left: 32px;
  width: 200px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.artikel-button {
  padding: 8px 15px;
  background-color: #d2bc9b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-left: 10px;
}

.artikel-button:hover {
  background-color: #c0a989;
}

.toolbar-right {
  margin-left: auto;
  display: flex;
  gap: 5px;
}

/* Main content styles */
.artikel-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Left panel styles */
.product-list-panel {
  width: 320px;
  border-right: 1px solid #ddd;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  padding: 10px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #ddd;
}

.nummer-column {
  width: 100px;
  font-weight: 600;
  font-size: 14px;
}

.bezeichnung-column {
  flex: 1;
  font-weight: 600;
  font-size: 14px;
}

.product-list-container {
  overflow-y: auto;
  flex: 1;
}

.product-list-item {
  display: flex;
  font-size: 14px;
  cursor: pointer;
}

.product-list-item:hover {
  background-color: #f8f9fa;
}

.product-list-item.selected {
  background-color: #e6f2ff;
}

.product-list-item .nummer-column,
.product-list-item .bezeichnung-column {
  padding: 10px;
  border-bottom: 1px solid #eaeaea;
  font-weight: normal;
}

/* Right panel styles */
.product-details-panel {
  flex: 1;
  display: flex;
}

.details-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Tabs styles */
.tabs-container {
  margin: 10px 0 0 15px;
  display: inline-flex;
  height: 40px;
  align-items: center;
  background-color: #f8f9fa;
  padding: 4px;
  border-radius: 6px;
}

.tab-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: 500;
  color: #6c757d;
}

.tab-button.active {
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  color: #333;
}

/* Tab content styles */
.tab-content {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

.form-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  margin-bottom: 15px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.section-label {
  font-size: 14px;
  font-weight: 500;
}

.section-label-small {
  font-size: 14px;
  margin-right: 8px;
}

.section-actions {
  display: flex;
  gap: 5px;
  align-items: center;
}

.action-button {
  height: 24px;
  width: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
}

.action-button:hover {
  background-color: #f0f0f0;
}

.input-with-button {
  display: flex;
}

.form-input {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
}

.form-button {
  margin-left: 8px;
  height: 40px;
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
}

.form-button:hover {
  background-color: #f0f0f0;
}

.form-textarea {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  height: 160px;
  resize: vertical;
}

.two-column-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.checkbox-field {
  display: flex;
  align-items: center;
}

.form-checkbox {
  height: 16px;
  width: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.checkbox-label {
  margin-left: 8px;
  font-size: 14px;
}

.labeled-input {
  display: flex;
  align-items: center;
}

.input-label {
  width: 100px;
  font-size: 14px;
}

.small-input {
  width: 60px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 4px;
}

.medium-input {
  width: 100px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 4px;
  margin-left: 8px;
}

.form-field {
  margin-top: 16px;
}

.table-container {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  font-size: 14px;
  border-collapse: collapse;
}

.table-header {
  padding: 8px;
  text-align: left;
  font-weight: 500;
  border-bottom: 1px solid #ddd;
  background-color: #f8f9fa;
}

.table-cell {
  padding: 8px;
  border-bottom: 1px solid #eaeaea;
}

.empty-message {
  font-size: 14px;
  color: #6c757d;
}

/* Side panel styles */
.side-panel {
  width: 300px;
  border-left: 1px solid #ddd;
  padding: 15px;
  position: relative;
}

.side-panel-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.publish-button-container {
  position: absolute;
  bottom: 15px;
  right: 15px;
}

.publish-button {
  background-color: #d2bc9b;
  color: white;
  border: none;
  padding: 8px 24px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.publish-button:hover {
  background-color: #c0a989;
}

.help-button-container {
  position: absolute;
  bottom: 80px;
  right: 30px;
}

.help-button {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #d2bc9b;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
}

/* Icon sizes */
.icon-small {
  height: 16px;
  width: 16px;
}

.icon-tiny {
  height: 12px;
  width: 12px;
}
</style>