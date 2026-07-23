import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Football TicTacToe GDD",
  description: "Complete Game Design Document & Architecture",
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Game Modes', link: '/guide/game-modes/tictactoe-4x4' },
      { text: 'Economy & Systems', link: '/guide/systems/economy-gems-chips' },
      { text: 'Project Notes', link: '/architecture/overview' }
    ],

    sidebar: [
      {
        text: 'Core Architecture',
        collapsed: true,
        items: [
          { text: 'Getting Started', link: '/guide/getting-started' },
          { text: 'General Architecture', link: '/guide/architecture' },
          { text: 'Database Structure', link: '/guide/database' },
          { text: 'Scraper Infrastructure', link: '/guide/scraper-api' },
          { text: 'Backend API & Sockets', link: '/guide/backend' },
          { text: 'Frontend Architecture', link: '/guide/frontend' }
        ]
      },
      {
        text: 'Game Modes (10 Modes)',
        items: [
          { text: '1. İstatistik Hedefleri', link: '/guide/game-modes/stats-target' },
          { text: '2. En X Kadroyu Kur', link: '/guide/game-modes/extreme-squad' },
          { text: '3. 4x4 TicTacToe', link: '/guide/game-modes/tictactoe-4x4' },
          { text: '4. Top 10 Tahmin', link: '/guide/game-modes/top-10-guess' },
          { text: '5. 2 Takım/Ülkeden Bul', link: '/guide/game-modes/find-player-from-two' },
          { text: '6. Transferlerden Tahmin', link: '/guide/game-modes/career-guess' },
          { text: '7. Piramit Sıralaması', link: '/guide/game-modes/pyramid-ranking' },
          { text: '8. Baş Harflerinden Bul', link: '/guide/game-modes/initials-guess' },
          { text: '9. Bayraklarla İlk 11', link: '/guide/game-modes/flag-eleven' },
          { text: '10. Oyuncular-Takımlar Örgüsü', link: '/guide/game-modes/chain-reaction' },
          { text: 'Ortak Multiplayer Sistemi', link: '/guide/game-modes/multiplayer-core' }
        ]
      },
      {
        text: 'Oyun Ekonomisi ve Sistemler',
        items: [
          { text: 'Gems & Chips Ekonomisi', link: '/guide/systems/economy-gems-chips' },
          { text: 'Level & Avatar Sistemi', link: '/guide/systems/level-system-avatars' },
          { text: 'Rank (ELO) Sistemi', link: '/guide/systems/ranking-elo' },
          { text: 'Sosyal & Liderlik Tabloları', link: '/guide/systems/social-leaderboards' }
        ]
      },
      {
        text: 'Proje Notları',
        collapsed: true,
        items: [
          {
            text: 'Mimari (Klasör Yapısı / Katmanlar)',
            items: [
              { text: 'Genel Bakış', link: '/architecture/overview' },
              { text: 'Frontend', link: '/architecture/frontend' },
              { text: 'Backend', link: '/architecture/backend' },
              { text: 'Database', link: '/architecture/database' }
            ]
          },
          {
            text: 'Kararlar (ADR)',
            items: [
              { text: '001 - Kimlik Doğrulama', link: '/decisions/001-auth' },
              { text: '002 - State Yönetimi', link: '/decisions/002-state-management' },
              { text: '003 - API Şekli', link: '/decisions/003-api' }
            ]
          },
          {
            text: 'Özellikler',
            items: [
              { text: 'Authentication', link: '/features/authentication' },
              { text: 'Profile', link: '/features/profile' },
              { text: 'Notifications', link: '/features/notifications' }
            ]
          },
          { text: 'Roadmap', link: '/roadmap' },
          { text: 'Current Task', link: '/current-task' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ]
  }
})
