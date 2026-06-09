const axios = require('axios');

class EveOnionPublisher {
  constructor(siteUrl, username, applicationPassword) {
    this.siteUrl = siteUrl;
    this.username = username;
    this.applicationPassword = applicationPassword;
    this.auth = {
      username: this.username,
      password: this.applicationPassword
    };
  }

  async createPost(title, content, status = 'publish') {
    const postData = {
      title: title,
      content: content,
      status: status,
      format: 'standard',
      categories: [], // Could add category IDs here
      tags: [] // Could add tag IDs here
    };

    try {
      const response = await axios.post(
        `${this.siteUrl}/wp-json/wp/v2/posts`,
        postData,
        { auth: this.auth }
      );

      console.log(`Post created successfully!`);
      console.log(`Title: ${response.data.title.rendered}`);
      console.log(`URL: ${response.data.link}`);
      console.log(`ID: ${response.data.id}`);

      return response.data;
    } catch (error) {
      console.error('Error creating post:', error.response?.data || error.message);
      throw error;
    }
  }
}

// Usage example:
async function publishEveOnionArticle() {
  // These would need to be configured properly
  const publisher = new EveOnionPublisher(
    process.env.WORDPRESS_SITE_URL || 'https://eveonion.com',
    process.env.WORDPRESS_USERNAME || 'your_username',
    process.env.WORDPRESS_APPLICATION_PASSWORD || 'your_app_password'
  );

  const title = "CCP Games Releases New Expansion Pack \"Real Life\" That Players Immediately Regret Purchasing";
  
  const content = `# CCP Games Releases New Expansion Pack "Real Life" That Players Immediately Regret Purchasing

**NEW HELGENETTE, EVE ONLINE** - In a surprise move that has shocked the gaming community, CCP Games announced the release of their latest expansion pack titled "Real Life," which players report is significantly more challenging and expensive than any previous content update.

The expansion, which became available to all accounts overnight, requires players to log out of the game permanently and manage responsibilities such as paying bills, maintaining relationships, and getting adequate sleep—all without the comfort of isk-generating afk ratting mechanics.

"I thought I was prepared for endgame content," said capsuleer "Mining_Mike47," who has been struggling with Real Life for approximately 30 years. "I've soloed supercapital fleets and held sovereignty, but somehow I still can't figure out how to maintain a steady income without taxes or understand why the NPCs in this expansion are so hostile when I don't respond to their quests immediately."

Players report that the expansion pack features extremely difficult survival mechanics, including the need to consume food every few hours, obtain 6-8 hours of sleep nightly, and participate in conversations where the primary reward appears to be emotional fulfillment rather than loot drops.

"The hardest part about Real Life is that there's no reset timer," explained longtime EVE player "DPS_Dan_99." "In wormholes, if you mess up, you can always dock up and try again. But in Real Life, mistakes compound and seem to affect your character permanently."

The expansion has also introduced new, unforgiving time management mechanics, where players cannot simply queue up 24 hours of offline skill training to gain advantages while away from the game.

CCP Games responded to complaints by stating that Real Life is "intended to be challenging" and that "some players may find ways to balance it with other activities," though they acknowledged that many players appear to have "soft-locked themselves" by purchasing the expansion too early in their gaming careers.

The expansion pack has received mixed reviews, with a current Metacritic score of 3.2/10 from players who report that the content feels "grindy," "expensive," and "lacking in proper endgame progression."

However, some veteran players have noted that completing significant progress in Real Life can lead to unique rewards such as property ownership, meaningful relationships, and financial stability—though these endgame objectives reportedly take significantly longer to achieve than obtaining a fully supercapital fleet in EVE Online.`;

  try {
    const post = await publisher.createPost(title, content);
    console.log("EveOnion article published successfully!");
    console.log(`Post URL: ${post.link}`);
    console.log(`Post Title: ${post.title.rendered}`);
    
    return {
      url: post.link,
      title: post.title.rendered
    };
  } catch (error) {
    console.error("Failed to publish EveOnion article:", error);
    throw error;
  }
}

module.exports = EveOnionPublisher;

if (require.main === module) {
  publishEveOnionArticle()
    .then(result => {
      console.log("Publication completed:", result);
    })
    .catch(error => {
      console.error("Publication failed:", error);
    });
}