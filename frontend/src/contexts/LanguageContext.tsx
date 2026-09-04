import React, { createContext, useContext, useState } from 'react';

export type Language = 'en' | 'kn' | 'hi';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const TRANSLATIONS: Record<Language, Record<string, string>> = {
  en: {
    farmAdvisory: 'Farm Advisory',
    welcome: 'Welcome',
    planCrop: 'Plan a Crop',
    cropSimulator3d: 'Crop Simulator 3D',
    seeSimulateSucceed: 'See. Simulate. Succeed.',
    soil: 'Soil',
    water: 'Water',
    season: 'Season',
    location: 'Location',
    startNewSimulation: 'Start New Simulation',
    bestMatch: 'Best Match',
    suitabilityScore: 'Suitability Score',
    peerEvidenceTitle: 'Regional Peer Evidence & Farmer Network',
    peerEvidenceDesc: 'Real results & evidence from verified regional farmers growing recommended oilseeds.',
    offlineSupport: 'Offline Support',
    myFarmProfile: 'My Farm Profile',
    profitAndMarket: 'Profit & Market Intelligence',
    marketplace: 'Marketplace',
    mapExplorer: 'Map Explorer & Mandi Reach',
    subsidies: 'Subsidies & Schemes',
    offlineSupportDesc: 'Works over a cellular phone call without internet',
    languageSelect: 'Language',
  },
  kn: {
    farmAdvisory: 'ಸಲಹೆ',
    welcome: 'ಸ್ವಾಗತ',
    planCrop: 'ಬೆಳೆ ಯೋಜನೆ ಮಾಡಿ',
    cropSimulator3d: '3D ಬೆಳೆ ಸಿಮ್ಯುಲೇಟರ್',
    seeSimulateSucceed: 'ನೋಡಿ. ಸಿಮ್ಯುಲೇಟ್ ಮಾಡಿ. ಗೆಲ್ಲಿರಿ.',
    soil: 'ಮಣ್ಣು',
    water: 'ನೀರು',
    season: 'ಋತು',
    location: 'ಸ್ಥಳ',
    startNewSimulation: 'ಹೊಸ ಸಿಮ್ಯುಲೇಶನ್ ಪ್ರಾರಂಭಿಸಿ',
    bestMatch: 'ಅತ್ಯುತ್ತಮ ಬೆಳೆ',
    suitabilityScore: 'ಸೂಕ್ತತೆ ಅಂಕ',
    peerEvidenceTitle: 'ಪ್ರಾದೇಶಿಕ ರೈತರ ಸಾಕ್ಷ್ಯ ಮತ್ತು ಜಾಲ',
    peerEvidenceDesc: 'ಶಿಫಾರಸು ಮಾಡಿದ ಎಣ್ಣೆಕಾಳು ಬೆಳೆಯುವ ಪ್ರಾದೇಶಿಕ ರೈತರ ಫಲಿತಾಂಶಗಳು.',
    offlineSupport: 'ಆಫ್‌ಲೈನ್ ಬೆಂಬಲ',
    myFarmProfile: 'ನನ್ನ ಜಮೀನು ಪ್ರೊಫೈಲ್',
    profitAndMarket: 'ಲಾಭ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಮಾಹಿತಿ',
    marketplace: 'ಮಾರುಕಟ್ಟೆ ಕ್ಷೇತ್ರ',
    mapExplorer: 'ಮ್ಯಾಪ್ ಮತ್ತು ಮಂಡಿ ತಲುಪು',
    subsidies: 'ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು',
    offlineSupportDesc: 'ಇಂಟರ್ನೆಟ್ ಇಲ್ಲದೆ ಫೋನ್ ಕಾಲ್ ಮೂಲಕ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ',
    languageSelect: 'ಭಾಷೆ',
  },
  hi: {
    farmAdvisory: 'कृषि परामर्श',
    welcome: 'स्वागत है',
    planCrop: 'फसल की योजना बनाएं',
    cropSimulator3d: '3D फसल सिम्युलेटर',
    seeSimulateSucceed: 'देखें। अनुकरण करें। सफल हों।',
    soil: 'मिट्टी',
    water: 'पानी',
    season: 'मौसम',
    location: 'स्थान',
    startNewSimulation: 'नया सिमुलेशन शुरू करें',
    bestMatch: 'सर्वश्रेष्ठ मिलान',
    suitabilityScore: 'उपयुक्तता स्कोर',
    peerEvidenceTitle: 'क्षेत्रीय किसान साक्ष्य और नेटवर्क',
    peerEvidenceDesc: 'अनुशंसित तिलहन उगाने वाले क्षेत्रीय किसानों के परिणाम।',
    offlineSupport: 'ऑफ़लाइन सहायता',
    myFarmProfile: 'मेरा खेत प्रोफ़ाइल',
    profitAndMarket: 'लाभ और बाजार आसूचना',
    marketplace: 'बाज़ार स्थान',
    mapExplorer: 'मानचित्र और मंडी पहुँच',
    subsidies: 'सरकारी योजनाएं',
    offlineSupportDesc: 'बिना इंटरनेट के फोन कॉल पर काम करता है',
    languageSelect: 'भाषा',
  },
};

const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key: string) => key,
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    return (localStorage.getItem('cropshift_language') as Language) || 'en';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('cropshift_language', lang);
  };

  const t = (key: string): string => {
    return TRANSLATIONS[language]?.[key] || TRANSLATIONS.en[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
