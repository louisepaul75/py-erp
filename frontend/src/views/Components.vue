<template>
    <div class="components-page">
        <h1>UI Components Style Guide</h1>
        <p class="subtitle">Reference for all UI components used in the pyERP project</p>

        <div class="component-section">
            <h2>Buttons</h2>
            <div class="component-group">
                <div class="component-item">
                    <h3>Primary Button</h3>
                    <v-btn color="primary">Primary Button</v-btn>
                    <code>v-btn color="primary"</code>
                </div>
                <div class="component-item">
                    <h3>Secondary Button</h3>
                    <v-btn color="secondary">Secondary Button</v-btn>
                    <code>v-btn color="secondary"</code>
                </div>
                <div class="component-item">
                    <h3>Outlined Button</h3>
                    <v-btn variant="outlined" color="primary">Outlined Button</v-btn>
                    <code>v-btn variant="outlined" color="primary"</code>
                </div>
                <div class="component-item">
                    <h3>Text Button</h3>
                    <v-btn variant="text" color="primary">Text Button</v-btn>
                    <code>v-btn variant="text" color="primary"</code>
                </div>
                <div class="component-item">
                    <h3>Icon Button</h3>
                    <v-btn icon="mdi-plus" color="primary"></v-btn>
                    <code>v-btn icon="mdi-plus" color="primary"</code>
                </div>
            </div>
        </div>

        <div class="component-section">
            <h2>Text Fields</h2>
            <div class="component-group">
                <div class="component-item">
                    <h3>Basic Input</h3>
                    <v-text-field label="Basic Input" placeholder="Enter text"></v-text-field>
                    <code>v-text-field label="Basic Input" placeholder="Enter text"</code>
                </div>
                <div class="component-item">
                    <h3>With Icon</h3>
                    <v-text-field label="With Icon" prepend-icon="mdi-account"></v-text-field>
                    <code>v-text-field label="With Icon" prepend-icon="mdi-account"</code>
                </div>
                <div class="component-item">
                    <h3>Required Field</h3>
                    <v-text-field label="Required Field" required></v-text-field>
                    <code>v-text-field label="Required Field" required</code>
                </div>
                <div class="component-item">
                    <h3>Textarea</h3>
                    <v-textarea label="Textarea" rows="3"></v-textarea>
                    <code>v-textarea label="Textarea" rows="3"</code>
                </div>
            </div>
        </div>

        <div class="component-section">
            <h2>Cards</h2>
            <div class="component-group">
                <div class="component-item wide">
                    <h3>Basic Card</h3>
                    <v-card>
                        <v-card-title>Card Title</v-card-title>
                        <v-card-text>
                            This is the content of the card. It can contain any information that needs to be displayed.
                        </v-card-text>
                        <v-card-actions>
                            <v-btn color="primary">Action</v-btn>
                        </v-card-actions>
                    </v-card>
                    <code>v-card with v-card-title, v-card-text, and v-card-actions</code>
                </div>
                <div class="component-item wide">
                    <h3>Elevated Card</h3>
                    <v-card elevation="4">
                        <v-card-title>Elevated Card</v-card-title>
                        <v-card-text>
                            This card has an elevation of 4, giving it a shadow effect.
                        </v-card-text>
                    </v-card>
                    <code>v-card elevation="4"</code>
                </div>
            </div>
        </div>

        <div class="component-section">
            <h2>Data Display</h2>
            <div class="component-group">
                <div class="component-item wide">
                    <h3>Simple Table</h3>
                    <v-table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>John Doe</td>
                                <td>john@example.com</td>
                                <td>Active</td>
                            </tr>
                            <tr>
                                <td>Jane Smith</td>
                                <td>jane@example.com</td>
                                <td>Pending</td>
                            </tr>
                        </tbody>
                    </v-table>
                    <code>v-table with thead and tbody</code>
                </div>
            </div>
        </div>

        <div class="component-section">
            <h2>Color Palette</h2>
            <div class="color-grid">
                <div class="color-item primary">
                    <div class="color-swatch"></div>
                    <div class="color-info">
                        <h3>Primary</h3>
                        <code>color="primary"</code>
                    </div>
                </div>
                <div class="color-item secondary">
                    <div class="color-swatch"></div>
                    <div class="color-info">
                        <h3>Secondary</h3>
                        <code>color="secondary"</code>
                    </div>
                </div>
                <div class="color-item success">
                    <div class="color-swatch"></div>
                    <div class="color-info">
                        <h3>Success</h3>
                        <code>color="success"</code>
                    </div>
                </div>
                <div class="color-item info">
                    <div class="color-swatch"></div>
                    <div class="color-info">
                        <h3>Info</h3>
                        <code>color="info"</code>
                    </div>
                </div>
                <div class="color-item warning">
                    <div class="color-swatch"></div>
                    <div class="color-info">
                        <h3>Warning</h3>
                        <code>color="warning"</code>
                    </div>
                </div>
                <div class="color-item error">
                    <div class="color-swatch"></div>
                    <div class="color-info">
                        <h3>Error</h3>
                        <code>color="error"</code>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// Component setup
</script>

<style scoped>
.components-page {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.subtitle {
    color: #666;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}

.component-section {
    margin-bottom: 3rem;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 20px;
    background-color: #fff;
}

.component-section h2 {
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.component-group {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
}

.component-item {
    flex: 1 1 300px;
    padding: 15px;
    border: 1px solid #eee;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.component-item.wide {
    flex: 1 1 600px;
}

.component-item h3 {
    margin-bottom: 10px;
    font-size: 1rem;
}

.component-item code {
    margin-top: 10px;
    display: block;
    padding: 8px;
    background-color: #f5f5f5;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #333;
}

.color-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
}

.color-item {
    display: flex;
    align-items: center;
    gap: 15px;
}

.color-swatch {
    width: 60px;
    height: 60px;
    border-radius: 4px;
}

.color-item.primary .color-swatch {
    background-color: var(--v-theme-primary);
}

.color-item.secondary .color-swatch {
    background-color: var(--v-theme-secondary);
}

.color-item.success .color-swatch {
    background-color: var(--v-theme-success);
}

.color-item.info .color-swatch {
    background-color: var(--v-theme-info);
}

.color-item.warning .color-swatch {
    background-color: var(--v-theme-warning);
}

.color-item.error .color-swatch {
    background-color: var(--v-theme-error);
}

.color-info {
    flex: 1;
}

.color-info h3 {
    margin-bottom: 5px;
}
</style> 