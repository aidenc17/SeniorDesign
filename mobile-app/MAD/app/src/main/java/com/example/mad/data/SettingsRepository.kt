package com.example.mad.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

data class SettingsData(
    val regularUrl: String,
    val authenticatedUrl: String
)

private val Context.settingsDataStore: DataStore<Preferences> by preferencesDataStore(
    name = "settings"
)

class SettingsRepository(context: Context) {
    private val dataStore = context.settingsDataStore

    private val regularUrlKey = stringPreferencesKey("regular_url")
    private val authenticatedUrlKey = stringPreferencesKey("authenticated_url")

    val settingsFlow: Flow<SettingsData> = dataStore.data.map { preferences ->
        SettingsData(
            regularUrl = preferences[regularUrlKey].orEmpty(),
            authenticatedUrl = preferences[authenticatedUrlKey].orEmpty()
        )
    }

    suspend fun saveUrls(regularUrl: String, authenticatedUrl: String) {
        dataStore.edit { preferences ->
            preferences[regularUrlKey] = regularUrl
            preferences[authenticatedUrlKey] = authenticatedUrl
        }
    }
}
